from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.security import create_access_token, get_password_hash
from main import app
from models.user import RoleEnum, User


def _build_session_factory(tmp_path: Path):
    db_path = tmp_path / "settings-permission-management.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return testing_session_local


def _seed_users(session_factory):
    session = session_factory()
    admin = User(
        username="perm-admin",
        password_hash=get_password_hash("Admin@2026"),
        role=RoleEnum.ADMIN,
        name="权限管理员",
        phone="13800138000",
    )
    manager = User(
        username="perm-manager",
        password_hash=get_password_hash("Manager@2026"),
        role=RoleEnum.MANAGER,
        name="权限经理",
        phone="13900139000",
    )
    session.add_all([admin, manager])
    session.commit()
    session.refresh(admin)
    session.refresh(manager)
    session.close()
    return admin, manager


def _auth_header(user: User):
    token = create_access_token({"sub": user.username})
    return {"Authorization": f"Bearer {token}"}


def _extract_data(response):
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 200, body
    return body["data"]


def test_permission_catalog_and_role_template_roundtrip(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    admin, manager = _seed_users(session_factory)
    client = TestClient(app)
    admin_headers = _auth_header(admin)

    catalog = _extract_data(client.get("/api/v1/users/permission-catalog", headers=admin_headers))
    assert any(module["module_key"] == "permission_management" for module in catalog["modules"])
    assert "settings.permission_management.access" in catalog["role_templates"]["ADMIN"]
    assert "settings.permission_management.access" not in catalog["role_templates"]["MANAGER"]

    updated_role = _extract_data(
        client.put(
            f"/api/v1/users/roles/{manager.role.value}/permissions",
            json={
                "permissions": [
                    "settings.permission_management.access",
                    "settings.permission_management.detail.view",
                ]
            },
            headers=admin_headers,
        )
    )
    assert updated_role["role"] == "MANAGER"
    assert updated_role["permissions"] == [
        "settings.permission_management.access",
        "settings.permission_management.detail.view",
    ]

    detail = _extract_data(client.get(f"/api/v1/users/{manager.id}/permissions", headers=admin_headers))
    assert detail["user"]["id"] == manager.id
    assert detail["role_permissions"] == [
        "settings.permission_management.access",
        "settings.permission_management.detail.view",
    ]


def test_user_permission_overrides_affect_effective_permissions_and_login_payload(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    admin, manager = _seed_users(session_factory)
    client = TestClient(app)
    admin_headers = _auth_header(admin)

    _extract_data(
        client.put(
            f"/api/v1/users/roles/{manager.role.value}/permissions",
            json={
                "permissions": [
                    "settings.permission_management.access",
                    "settings.permission_management.detail.view",
                    "settings.reports.access",
                    "settings.reports.download",
                ]
            },
            headers=admin_headers,
        )
    )

    updated_override = _extract_data(
        client.put(
            f"/api/v1/users/{manager.id}/permissions",
            json={
                "allow_permissions": ["settings.brand_config.access"],
                "deny_permissions": ["settings.reports.download"],
            },
            headers=admin_headers,
        )
    )
    assert updated_override["user_overrides"]["allow_permissions"] == ["settings.brand_config.access"]
    assert updated_override["user_overrides"]["deny_permissions"] == ["settings.reports.download"]
    assert "settings.brand_config.access" in updated_override["effective_permissions"]
    assert "settings.reports.download" not in updated_override["effective_permissions"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": manager.username, "password": "Manager@2026"},
    )
    login_data = _extract_data(login_response)
    assert login_data["user"]["role"] == "MANAGER"
    assert "settings.brand_config.access" in login_data["user"]["effective_permissions"]
    assert "settings.reports.download" not in login_data["user"]["effective_permissions"]


def test_permission_protected_settings_routes_use_effective_permissions(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    admin, manager = _seed_users(session_factory)
    client = TestClient(app)
    admin_headers = _auth_header(admin)
    manager_headers = _auth_header(manager)

    users_response = client.get("/api/v1/users", headers=manager_headers)
    assert users_response.status_code == 403

    _extract_data(
        client.put(
            f"/api/v1/users/roles/{manager.role.value}/permissions",
            json={"permissions": ["settings.permission_management.access"]},
            headers=admin_headers,
        )
    )

    users_response = client.get("/api/v1/users", headers=manager_headers)
    users_data = _extract_data(users_response)
    assert users_data["total"] == 2

    brand_response = client.get("/api/v1/settings/platform", headers=manager_headers)
    assert brand_response.status_code == 403

    _extract_data(
        client.put(
            f"/api/v1/users/{manager.id}/permissions",
            json={
                "allow_permissions": ["settings.brand_config.access"],
                "deny_permissions": [],
            },
            headers=admin_headers,
        )
    )

    brand_response = client.get("/api/v1/settings/platform", headers=manager_headers)
    brand_data = _extract_data(brand_response)
    assert brand_data["system_name"]
