import json

from sqlalchemy.orm import Session

from core.audit import write_audit_log
from core.exceptions import BusinessError, NotFoundError
from core.permission_catalog import (
    ALL_SETTINGS_PERMISSION_KEYS,
    SETTINGS_PERMISSION_CATALOG,
    get_default_permissions_for_role,
)
from models.access_control import RolePermissionProfile, UserPermissionOverride
from models.user import RoleEnum, User


def _loads_permissions(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    try:
        loaded = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    if not isinstance(loaded, list):
        return []
    return [str(item) for item in loaded]


def _dumps_permissions(items: list[str]) -> str:
    return json.dumps(items, ensure_ascii=False)


class PermissionService:
    def __init__(self, db: Session):
        self.db = db

    def _normalize_permissions(self, permissions: list[str]) -> list[str]:
        normalized = sorted({str(item) for item in permissions if item})
        invalid = [item for item in normalized if item not in ALL_SETTINGS_PERMISSION_KEYS]
        if invalid:
            raise BusinessError(f"存在无效权限项: {', '.join(invalid)}")
        return normalized

    def ensure_role_templates(self):
        created = False
        for role in RoleEnum:
            profile = self.db.query(RolePermissionProfile).filter(RolePermissionProfile.role == role).first()
            if profile:
                continue
            created = True
            self.db.add(
                RolePermissionProfile(
                    role=role,
                    permissions_json=_dumps_permissions(get_default_permissions_for_role(role.value)),
                )
            )
        self.db.flush()
        if created:
            self.db.commit()

    def get_role_profile(self, role: str) -> RolePermissionProfile:
        self.ensure_role_templates()
        enum_role = RoleEnum(role)
        profile = self.db.query(RolePermissionProfile).filter(RolePermissionProfile.role == enum_role).first()
        if not profile:
            raise NotFoundError("角色权限模板不存在")
        return profile

    def get_role_permissions(self, role: str) -> list[str]:
        profile = self.get_role_profile(role)
        return _loads_permissions(profile.permissions_json)

    def get_user_override(self, user_id: int, create: bool = False) -> UserPermissionOverride | None:
        override = self.db.query(UserPermissionOverride).filter(UserPermissionOverride.user_id == user_id).first()
        if override or not create:
            return override

        override = UserPermissionOverride(
            user_id=user_id,
            allow_permissions_json="[]",
            deny_permissions_json="[]",
        )
        self.db.add(override)
        self.db.flush()
        return override

    def get_user_override_payload(self, user_id: int) -> dict:
        override = self.get_user_override(user_id, create=False)
        if not override:
            return {"allow_permissions": [], "deny_permissions": []}
        return {
            "allow_permissions": _loads_permissions(override.allow_permissions_json),
            "deny_permissions": _loads_permissions(override.deny_permissions_json),
        }

    def get_effective_permissions(self, user: User) -> list[str]:
        role_value = getattr(user.role, "value", user.role)
        role_permissions = set(self.get_role_permissions(role_value))
        override = self.get_user_override_payload(user.id)
        effective = (role_permissions | set(override["allow_permissions"])) - set(override["deny_permissions"])
        return sorted(effective)

    def get_user_permission_bundle(self, user: User) -> dict:
        role_value = getattr(user.role, "value", user.role)
        role_permissions = self.get_role_permissions(role_value)
        override = self.get_user_override_payload(user.id)
        return {
            "role_permissions": role_permissions,
            "user_overrides": override,
            "effective_permissions": self.get_effective_permissions(user),
        }

    def get_catalog_payload(self) -> dict:
        self.ensure_role_templates()
        role_templates = {
            role.value: self.get_role_permissions(role.value)
            for role in RoleEnum
        }
        return {
            "modules": SETTINGS_PERMISSION_CATALOG,
            "all_permission_keys": ALL_SETTINGS_PERMISSION_KEYS,
            "role_templates": role_templates,
        }

    def update_role_permissions(self, role: str, permissions: list[str], operator_id: int) -> dict:
        normalized = self._normalize_permissions(permissions)
        profile = self.get_role_profile(role)
        profile.permissions_json = _dumps_permissions(normalized)
        self.db.flush()
        write_audit_log(
            db=self.db,
            user_id=operator_id,
            action="UPDATE",
            table_name="role_permission_profiles",
            record_id=profile.id,
            new_value={"role": role, "permissions": normalized},
        )
        self.db.commit()
        return {"role": role, "permissions": normalized}

    def update_user_override(self, user_id: int, allow_permissions: list[str], deny_permissions: list[str], operator_id: int) -> dict:
        normalized_allow = self._normalize_permissions(allow_permissions)
        normalized_deny = self._normalize_permissions(deny_permissions)
        overlap = sorted(set(normalized_allow) & set(normalized_deny))
        if overlap:
            raise BusinessError(f"同一权限不能同时被授予和禁用: {', '.join(overlap)}")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户未找到")

        override = self.get_user_override(user_id, create=True)
        override.allow_permissions_json = _dumps_permissions(normalized_allow)
        override.deny_permissions_json = _dumps_permissions(normalized_deny)
        self.db.flush()
        write_audit_log(
            db=self.db,
            user_id=operator_id,
            action="UPDATE",
            table_name="user_permission_overrides",
            record_id=override.id,
            new_value={
                "user_id": user_id,
                "allow_permissions": normalized_allow,
                "deny_permissions": normalized_deny,
            },
        )
        self.db.commit()
        return self.get_user_permission_detail(user_id)

    def get_user_permission_detail(self, user_id: int) -> dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户未找到")
        bundle = self.get_user_permission_bundle(user)
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "role": getattr(user.role, "value", user.role),
                "phone": user.phone,
            },
            **bundle,
        }
