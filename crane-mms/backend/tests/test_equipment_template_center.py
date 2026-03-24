from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.security import create_access_token
from main import app
from models.customer import Customer
from models.user import RoleEnum, User


def _build_session_factory(tmp_path: Path):
    db_path = tmp_path / "equipment-template-center.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return testing_session_local


def _seed_admin_and_customer(session_factory):
    session = session_factory()
    admin = User(
        username="template-admin",
        password_hash="not-used",
        role=RoleEnum.ADMIN,
        name="模板管理员",
        phone="13800138000",
    )
    customer = Customer(
        company_name="模板测试客户",
        contact_name="李主管",
        contact_phone="13900139000",
        address="上海市模板路 18 号",
        login_phone="13900139000",
    )
    session.add(admin)
    session.add(customer)
    session.commit()
    session.refresh(admin)
    session.refresh(customer)
    session.close()
    return admin, customer


def _auth_header(user: User):
    token = create_access_token({"sub": user.username})
    return {"Authorization": f"Bearer {token}"}


def _extract_data(response):
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 200, body
    return body["data"]


def _create_group(client: TestClient, headers: dict):
    response = client.post(
        "/api/v1/equipment-template-groups",
        json={
            "category": "桥式起重机",
            "model_type": "QD型",
            "name": "桥式起重机-QD 模板组",
        },
        headers=headers,
    )
    return _extract_data(response)


def _create_version(client: TestClient, headers: dict, group_id: int, **overrides):
    payload = {
        "group_id": group_id,
        "name": "QD-通用范围模板",
        "manufacturer": None,
        "tonnage_rule_type": "RANGE",
        "tonnage_exact": None,
        "tonnage_min": 8,
        "tonnage_max": 12,
        "span_rule_type": "RANGE",
        "span_exact": None,
        "span_min": 15,
        "span_max": 20,
        "default_params": {
            "tonnage": "10t",
            "span": "16.5m",
            "lifting_height": "9m",
            "work_class": "A5",
            "installation_location": "一号厂房",
        },
        "parts": [
            {"part_name": "主梁", "specification": "Q235B", "quantity": 1},
            {"part_name": "吊钩组", "specification": "10t", "quantity": 1},
        ],
        "inspection_items": [
            {"item_name": "钢丝绳检查", "description": "检查磨损、断丝情况", "required": True},
            {"item_name": "制动器检查", "description": "检查间隙与制动力", "required": True},
        ],
        "version_note": "初始化版本",
        "base_template_id": None,
    }
    payload.update(overrides)
    response = client.post(
        "/api/v1/equipment-template-versions",
        json=payload,
        headers=headers,
    )
    return response


def test_match_prefers_range_then_manufacturer(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    admin, _ = _seed_admin_and_customer(session_factory)
    client = TestClient(app)
    headers = _auth_header(admin)

    group = _create_group(client, headers)
    _extract_data(_create_version(client, headers, group["id"]))
    _extract_data(
        _create_version(
            client,
            headers,
            group["id"],
            name="QD-厂家范围模板",
            manufacturer="沪工",
            parts=[{"part_name": "厂家专用卷筒", "specification": "沪工定制", "quantity": 1}],
        )
    )
    _extract_data(
        _create_version(
            client,
            headers,
            group["id"],
            name="QD-精确模板",
            manufacturer="沪工",
            tonnage_rule_type="EXACT",
            tonnage_exact="10t",
            tonnage_min=None,
            tonnage_max=None,
            span_rule_type="EXACT",
            span_exact="16.5m",
            span_min=None,
            span_max=None,
        )
    )

    response = client.get(
        "/api/v1/equipment-template-match",
        params={
            "category": "桥式起重机",
            "model_type": "QD型",
            "tonnage": "10t",
            "span": "16.5m",
            "manufacturer": "沪工",
        },
        headers=headers,
    )

    data = _extract_data(response)
    assert data["matched"] is True
    assert data["template_name"] == "QD-厂家范围模板"
    assert data["manufacturer"] == "沪工"
    assert data["match_summary"]["rule_priority"] == "RANGE_FIRST"
    assert data["parts"][0]["part_name"] == "厂家专用卷筒"


def test_create_template_version_rejects_overlapping_ranges(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    admin, _ = _seed_admin_and_customer(session_factory)
    client = TestClient(app)
    headers = _auth_header(admin)

    group = _create_group(client, headers)
    _extract_data(_create_version(client, headers, group["id"]))

    response = _create_version(
        client,
        headers,
        group["id"],
        name="QD-重叠范围模板",
        tonnage_min=10,
        tonnage_max=14,
        span_min=16,
        span_max=22,
    )

    assert response.status_code == 400, response.text
    assert "重叠" in response.json()["msg"]


def test_create_equipment_with_candidate_flag_generates_candidate_snapshot(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    admin, customer = _seed_admin_and_customer(session_factory)
    client = TestClient(app)
    headers = _auth_header(admin)

    group = _create_group(client, headers)
    version = _extract_data(
        _create_version(
            client,
            headers,
            group["id"],
            manufacturer="沪工",
            inspection_items=[
                {"item_name": "钢丝绳检查", "description": "模板项", "required": True},
            ],
        )
    )

    response = client.post(
        "/api/v1/equipments",
        json={
            "customer_id": customer.id,
            "category": "桥式起重机",
            "model_type": "QD型",
            "name": "客户A-1号行车",
            "manufacturer": "沪工",
            "tonnage": "10t",
            "span": "16.5m",
            "lifting_height": "12m",
            "work_class": "A5",
            "installation_location": "一号车间",
            "parts": [
                {"part_name": "主梁", "specification": "Q235B", "quantity": 1},
                {"part_name": "新增导绳器", "specification": "加强型", "quantity": 1},
            ],
            "inspection_items": [
                {"item_name": "钢丝绳检查", "description": "模板项", "required": True},
                {"item_name": "导绳器检查", "description": "手工补录项", "required": True},
            ],
            "applied_template_id": group["id"],
            "applied_template_version": version["version"],
            "submit_as_template_candidate": True,
        },
        headers=headers,
    )

    equipment = _extract_data(response)
    assert equipment["manufacturer"] == "沪工"
    assert equipment["submit_as_template_candidate"] is True

    candidate_response = client.get("/api/v1/equipment-template-candidates", headers=headers)
    candidates = _extract_data(candidate_response)
    assert len(candidates) == 1
    assert candidates[0]["equipment_id"] == equipment["id"]
    assert candidates[0]["status"] == "PENDING_REVIEW"
    assert any(diff["field"] == "parts" for diff in candidates[0]["diff_summary"])
    assert any(diff["field"] == "inspection_items" for diff in candidates[0]["diff_summary"])


def test_approving_candidate_creates_new_template_version(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    admin, customer = _seed_admin_and_customer(session_factory)
    client = TestClient(app)
    headers = _auth_header(admin)

    group = _create_group(client, headers)
    version = _extract_data(
        _create_version(
            client,
            headers,
            group["id"],
            manufacturer="沪工",
            inspection_items=[{"item_name": "钢丝绳检查", "description": "模板项", "required": True}],
        )
    )

    equipment = _extract_data(
        client.post(
            "/api/v1/equipments",
            json={
                "customer_id": customer.id,
                "category": "桥式起重机",
                "model_type": "QD型",
                "name": "客户A-2号行车",
                "manufacturer": "沪工",
                "tonnage": "10t",
                "span": "16.5m",
                "lifting_height": "12m",
                "work_class": "A5",
                "installation_location": "二号车间",
                "parts": [{"part_name": "主梁", "specification": "Q235B", "quantity": 1}],
                "inspection_items": [
                    {"item_name": "钢丝绳检查", "description": "模板项", "required": True},
                    {"item_name": "导绳器检查", "description": "新版本项", "required": True},
                ],
                "applied_template_id": group["id"],
                "applied_template_version": version["version"],
                "submit_as_template_candidate": True,
            },
            headers=headers,
        )
    )

    candidates = _extract_data(client.get("/api/v1/equipment-template-candidates", headers=headers))
    candidate = candidates[0]

    response = client.post(
        f"/api/v1/equipment-template-candidates/{candidate['id']}/approve",
        json={"review_note": "导绳器检查已确认为通用要求"},
        headers=headers,
    )

    approval = _extract_data(response)
    assert approval["candidate_status"] == "APPROVED"
    assert approval["new_version"]["version"] == version["version"] + 1
    assert approval["new_version"]["status"] == "ACTIVE"
    assert approval["new_version"]["inspection_items"][-1]["item_name"] == "导绳器检查"

    original_version = _extract_data(
        client.get(f"/api/v1/equipment-template-versions/{version['id']}", headers=headers)
    )
    latest_version = _extract_data(
        client.get(f"/api/v1/equipment-template-versions/{approval['new_version']['id']}", headers=headers)
    )

    assert equipment["applied_template_id"] == group["id"]
    assert original_version["status"] == "HISTORY"
    assert latest_version["status"] == "ACTIVE"
