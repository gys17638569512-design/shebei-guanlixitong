from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.equipment import Equipment, EquipmentPart
from models.equipment_template import (
    EquipmentTemplateCandidate,
    EquipmentTemplateGroup,
    EquipmentTemplateVersion,
    InspectionBaseTemplate,
)


ACTIVE = "ACTIVE"
PENDING_REVIEW = "PENDING_REVIEW"
REJECTED = "REJECTED"
HISTORY = "HISTORY"


class EquipmentTemplateService:
    def __init__(self, db: Session):
        self.db = db

    def list_groups(self, category: str | None = None, model_type: str | None = None):
        query = self.db.query(EquipmentTemplateGroup)
        if category:
            query = query.filter(EquipmentTemplateGroup.category == category)
        if model_type:
            query = query.filter(EquipmentTemplateGroup.model_type == model_type)
        groups = query.order_by(EquipmentTemplateGroup.id.desc()).all()
        return [self.serialize_group(group) for group in groups]

    def create_group(self, payload, user_id: int):
        existing = (
            self.db.query(EquipmentTemplateGroup)
            .filter(
                EquipmentTemplateGroup.category == payload.category,
                EquipmentTemplateGroup.model_type == payload.model_type,
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="该设备大类与型式的模板组已存在")

        group = EquipmentTemplateGroup(
            category=payload.category,
            model_type=payload.model_type,
            name=payload.name,
            created_by=user_id,
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return self.serialize_group(group)

    def get_version(self, version_id: int):
        version = self.db.query(EquipmentTemplateVersion).filter(EquipmentTemplateVersion.id == version_id).first()
        if not version:
            raise HTTPException(status_code=404, detail="模板版本不存在")
        return self.serialize_version(version)

    def create_version(self, payload, user_id: int):
        group = self._get_group(payload.group_id)
        self._validate_rule_payload(payload)
        self._ensure_no_overlap(group.id, payload, exclude_version_id=None)

        version = EquipmentTemplateVersion(
            group_id=group.id,
            version=self._next_version_number(group.id),
            name=payload.name,
            manufacturer=self._normalize_manufacturer(payload.manufacturer),
            tonnage_rule_type=payload.tonnage_rule_type,
            tonnage_exact=payload.tonnage_exact,
            tonnage_min=payload.tonnage_min,
            tonnage_max=payload.tonnage_max,
            span_rule_type=payload.span_rule_type,
            span_exact=payload.span_exact,
            span_min=payload.span_min,
            span_max=payload.span_max,
            default_params_json=json.dumps(payload.default_params, ensure_ascii=False),
            parts_json=json.dumps(payload.parts, ensure_ascii=False),
            inspection_items_json=json.dumps(payload.inspection_items, ensure_ascii=False),
            status=ACTIVE,
            version_note=payload.version_note,
            base_template_id=payload.base_template_id,
            created_by=user_id,
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return self.serialize_version(version)

    def update_version(self, version_id: int, payload, user_id: int):
        current = self.db.query(EquipmentTemplateVersion).filter(EquipmentTemplateVersion.id == version_id).first()
        if not current:
            raise HTTPException(status_code=404, detail="模板版本不存在")

        self._validate_rule_payload(payload)
        self._ensure_no_overlap(current.group_id, payload, exclude_version_id=version_id)
        current.status = HISTORY

        successor = EquipmentTemplateVersion(
            group_id=current.group_id,
            version=self._next_version_number(current.group_id),
            name=payload.name,
            manufacturer=self._normalize_manufacturer(payload.manufacturer),
            tonnage_rule_type=payload.tonnage_rule_type,
            tonnage_exact=payload.tonnage_exact,
            tonnage_min=payload.tonnage_min,
            tonnage_max=payload.tonnage_max,
            span_rule_type=payload.span_rule_type,
            span_exact=payload.span_exact,
            span_min=payload.span_min,
            span_max=payload.span_max,
            default_params_json=json.dumps(payload.default_params, ensure_ascii=False),
            parts_json=json.dumps(payload.parts, ensure_ascii=False),
            inspection_items_json=json.dumps(payload.inspection_items, ensure_ascii=False),
            status=ACTIVE,
            version_note=payload.version_note,
            base_template_id=payload.base_template_id,
            created_by=user_id,
        )
        self.db.add(successor)
        self.db.commit()
        self.db.refresh(successor)
        return self.serialize_version(successor)

    def match_template(self, category: str, model_type: str, tonnage: str | None, span: str | None, manufacturer: str | None):
        group = (
            self.db.query(EquipmentTemplateGroup)
            .filter(
                EquipmentTemplateGroup.category == category,
                EquipmentTemplateGroup.model_type == model_type,
            )
            .first()
        )
        if not group:
            return {"matched": False, "message": "暂无对应模板组，请手工录入"}

        versions = (
            self.db.query(EquipmentTemplateVersion)
            .filter(
                EquipmentTemplateVersion.group_id == group.id,
                EquipmentTemplateVersion.status == ACTIVE,
            )
            .all()
        )
        matched_versions = [version for version in versions if self._match_rule(version, tonnage, span)]
        if not matched_versions:
            return {
                "matched": False,
                "group_id": group.id,
                "message": "模板组已存在，但未命中具体模板，请手工录入",
            }

        range_versions = [version for version in matched_versions if self._is_range_rule(version)]
        if range_versions:
            matched_versions = range_versions

        normalized_manufacturer = self._normalize_manufacturer(manufacturer)
        manufacturer_versions = [
            version for version in matched_versions if self._normalize_manufacturer(version.manufacturer) == normalized_manufacturer
        ]
        if manufacturer_versions:
            matched_versions = manufacturer_versions
        else:
            matched_versions = [
                version for version in matched_versions if self._normalize_manufacturer(version.manufacturer) is None
            ] or matched_versions

        matched_versions.sort(key=lambda item: (item.version, item.id), reverse=True)
        selected = matched_versions[0]
        serialized = self.serialize_version(selected)
        return {
            "matched": True,
            "group_id": group.id,
            "template_version_id": selected.id,
            "template_name": serialized["name"],
            "manufacturer": serialized["manufacturer"],
            "version": serialized["version"],
            "default_params": serialized["default_params"],
            "parts": serialized["parts"],
            "inspection_items": serialized["inspection_items"],
            "match_summary": {
                "rule_priority": "RANGE_FIRST",
                "tonnage_rule_type": serialized["tonnage_rule_type"],
                "span_rule_type": serialized["span_rule_type"],
                "is_manufacturer_specific": bool(serialized["manufacturer"]),
            },
        }

    def get_compatible_parts(self, category: str, model_type: str, tonnage: str | None = None, span: str | None = None, manufacturer: str | None = None):
        result = self.match_template(category, model_type, tonnage, span, manufacturer)
        return result["parts"] if result.get("matched") else []

    def create_candidate(self, payload, user_id: int):
        candidate = EquipmentTemplateCandidate(
            equipment_id=payload.equipment_id,
            group_id=payload.group_id,
            source_template_version_id=payload.source_template_version_id,
            submitted_by=user_id,
            status=PENDING_REVIEW,
            snapshot_json=json.dumps(payload.snapshot, ensure_ascii=False),
            diff_summary_json=json.dumps(payload.diff_summary, ensure_ascii=False),
        )
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return self.serialize_candidate(candidate)

    def create_candidate_from_equipment(self, equipment: Equipment, user_id: int):
        source_version = self._find_source_version(equipment.applied_template_id, equipment.applied_template_version)
        snapshot = self._build_candidate_snapshot(equipment, source_version)
        diff_summary = self._build_diff_summary(source_version, snapshot)
        candidate = EquipmentTemplateCandidate(
            equipment_id=equipment.id,
            group_id=source_version.group_id if source_version else equipment.applied_template_id,
            source_template_version_id=source_version.id if source_version else None,
            submitted_by=user_id,
            status=PENDING_REVIEW,
            snapshot_json=json.dumps(snapshot, ensure_ascii=False),
            diff_summary_json=json.dumps(diff_summary, ensure_ascii=False),
        )
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return self.serialize_candidate(candidate)

    def list_candidates(self):
        candidates = self.db.query(EquipmentTemplateCandidate).order_by(EquipmentTemplateCandidate.id.desc()).all()
        return [self.serialize_candidate(candidate) for candidate in candidates]

    def approve_candidate(self, candidate_id: int, user_id: int, review_note: str | None = None):
        candidate = self._get_candidate(candidate_id)
        if candidate.status != PENDING_REVIEW:
            raise HTTPException(status_code=400, detail="只有待审核候选可以通过")

        snapshot = json.loads(candidate.snapshot_json)
        source_version = candidate.source_template_version
        if source_version:
            source_version.status = HISTORY
            group_id = source_version.group_id
        else:
            group = self._find_or_create_group(
                snapshot["category"],
                snapshot["model_type"],
                snapshot.get("group_name") or f"{snapshot['category']}-{snapshot['model_type']} 模板组",
                user_id,
            )
            group_id = group.id

        self._ensure_no_overlap(group_id, self._dict_as_rule_payload(snapshot), exclude_version_id=source_version.id if source_version else None)
        version = EquipmentTemplateVersion(
            group_id=group_id,
            version=self._next_version_number(group_id),
            name=snapshot["name"],
            manufacturer=self._normalize_manufacturer(snapshot.get("manufacturer")),
            tonnage_rule_type=snapshot["tonnage_rule_type"],
            tonnage_exact=snapshot.get("tonnage_exact"),
            tonnage_min=snapshot.get("tonnage_min"),
            tonnage_max=snapshot.get("tonnage_max"),
            span_rule_type=snapshot["span_rule_type"],
            span_exact=snapshot.get("span_exact"),
            span_min=snapshot.get("span_min"),
            span_max=snapshot.get("span_max"),
            default_params_json=json.dumps(snapshot.get("default_params", {}), ensure_ascii=False),
            parts_json=json.dumps(snapshot.get("parts", []), ensure_ascii=False),
            inspection_items_json=json.dumps(snapshot.get("inspection_items", []), ensure_ascii=False),
            status=ACTIVE,
            version_note=review_note or snapshot.get("version_note"),
            base_template_id=snapshot.get("base_template_id"),
            created_by=user_id,
        )
        self.db.add(version)
        candidate.status = "APPROVED"
        candidate.review_note = review_note
        candidate.reviewed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(version)
        self.db.refresh(candidate)
        return {"candidate_status": candidate.status, "new_version": self.serialize_version(version)}

    def reject_candidate(self, candidate_id: int, review_note: str | None = None):
        candidate = self._get_candidate(candidate_id)
        candidate.status = REJECTED
        candidate.review_note = review_note
        candidate.reviewed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(candidate)
        return self.serialize_candidate(candidate)

    def list_base_templates(self, category: str | None = None, model_type: str | None = None):
        query = self.db.query(InspectionBaseTemplate)
        if category:
            query = query.filter(InspectionBaseTemplate.category == category)
        if model_type:
            query = query.filter(InspectionBaseTemplate.model_type == model_type)
        templates = query.order_by(InspectionBaseTemplate.id.desc()).all()
        return [self.serialize_base_template(item) for item in templates]

    def create_base_template(self, payload, user_id: int):
        self._validate_base_template(payload)
        template = InspectionBaseTemplate(
            category=payload.category,
            model_type=payload.model_type,
            name=payload.name,
            tonnage_rule_type=payload.tonnage_rule_type,
            tonnage_exact=payload.tonnage_exact,
            tonnage_min=payload.tonnage_min,
            tonnage_max=payload.tonnage_max,
            items_json=json.dumps(payload.items, ensure_ascii=False),
            note=payload.note,
            created_by=user_id,
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return self.serialize_base_template(template)

    def update_base_template(self, template_id: int, payload):
        self._validate_base_template(payload)
        template = self.db.query(InspectionBaseTemplate).filter(InspectionBaseTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="检修通用模板不存在")
        template.category = payload.category
        template.model_type = payload.model_type
        template.name = payload.name
        template.tonnage_rule_type = payload.tonnage_rule_type
        template.tonnage_exact = payload.tonnage_exact
        template.tonnage_min = payload.tonnage_min
        template.tonnage_max = payload.tonnage_max
        template.items_json = json.dumps(payload.items, ensure_ascii=False)
        template.note = payload.note
        self.db.commit()
        self.db.refresh(template)
        return self.serialize_base_template(template)

    def serialize_group(self, group: EquipmentTemplateGroup):
        return {
            "id": group.id,
            "category": group.category,
            "model_type": group.model_type,
            "name": group.name,
            "active_versions": [
                self.serialize_version(version)
                for version in sorted(group.versions, key=lambda item: (item.version, item.id), reverse=True)
            ],
        }

    def serialize_version(self, version: EquipmentTemplateVersion):
        return {
            "id": version.id,
            "group_id": version.group_id,
            "version": version.version,
            "name": version.name,
            "manufacturer": self._normalize_manufacturer(version.manufacturer),
            "tonnage_rule_type": version.tonnage_rule_type,
            "tonnage_exact": version.tonnage_exact,
            "tonnage_min": version.tonnage_min,
            "tonnage_max": version.tonnage_max,
            "span_rule_type": version.span_rule_type,
            "span_exact": version.span_exact,
            "span_min": version.span_min,
            "span_max": version.span_max,
            "default_params": self._load_json(version.default_params_json, {}),
            "parts": self._load_json(version.parts_json, []),
            "inspection_items": self._load_json(version.inspection_items_json, []),
            "status": version.status,
            "version_note": version.version_note,
            "base_template_id": version.base_template_id,
        }

    def serialize_candidate(self, candidate: EquipmentTemplateCandidate):
        equipment = candidate.equipment
        return {
            "id": candidate.id,
            "equipment_id": candidate.equipment_id,
            "equipment_name": equipment.name if equipment else None,
            "status": candidate.status,
            "group_id": candidate.group_id,
            "source_template_version_id": candidate.source_template_version_id,
            "snapshot": self._load_json(candidate.snapshot_json, {}),
            "diff_summary": self._load_json(candidate.diff_summary_json, []),
            "review_note": candidate.review_note,
            "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
        }

    def serialize_base_template(self, template: InspectionBaseTemplate):
        return {
            "id": template.id,
            "category": template.category,
            "model_type": template.model_type,
            "name": template.name,
            "tonnage_rule_type": template.tonnage_rule_type,
            "tonnage_exact": template.tonnage_exact,
            "tonnage_min": template.tonnage_min,
            "tonnage_max": template.tonnage_max,
            "items": self._load_json(template.items_json, []),
            "status": template.status,
            "note": template.note,
        }

    def _get_group(self, group_id: int):
        group = self.db.query(EquipmentTemplateGroup).filter(EquipmentTemplateGroup.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="模板组不存在")
        return group

    def _get_candidate(self, candidate_id: int):
        candidate = self.db.query(EquipmentTemplateCandidate).filter(EquipmentTemplateCandidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="模板候选不存在")
        return candidate

    def _validate_rule_payload(self, payload):
        self._validate_rule("吨位", payload.tonnage_rule_type, payload.tonnage_exact, payload.tonnage_min, payload.tonnage_max)
        self._validate_rule("跨度", payload.span_rule_type, payload.span_exact, payload.span_min, payload.span_max)

    def _validate_base_template(self, payload):
        self._validate_rule("吨位", payload.tonnage_rule_type, payload.tonnage_exact, payload.tonnage_min, payload.tonnage_max)

    def _validate_rule(self, label: str, rule_type: str, exact: Any, minimum: Any, maximum: Any):
        if rule_type == "EXACT":
            if exact in (None, ""):
                raise HTTPException(status_code=400, detail=f"{label}精确值不能为空")
        elif rule_type == "RANGE":
            if minimum is None or maximum is None:
                raise HTTPException(status_code=400, detail=f"{label}范围值不能为空")
            if minimum > maximum:
                raise HTTPException(status_code=400, detail=f"{label}范围最小值不能大于最大值")
        else:
            raise HTTPException(status_code=400, detail=f"{label}规则类型不合法")

    def _ensure_no_overlap(self, group_id: int, payload, exclude_version_id: int | None):
        manufacturer = self._normalize_manufacturer(payload.manufacturer)
        query = self.db.query(EquipmentTemplateVersion).filter(
            EquipmentTemplateVersion.group_id == group_id,
            EquipmentTemplateVersion.status == ACTIVE,
        )
        if exclude_version_id is not None:
            query = query.filter(EquipmentTemplateVersion.id != exclude_version_id)

        for version in query.all():
            if self._normalize_manufacturer(version.manufacturer) != manufacturer:
                continue
            if self._is_exact_supplement_pair(version, payload):
                continue
            if self._rules_overlap(version, payload):
                raise HTTPException(status_code=400, detail="模板范围配置与现有启用模板重叠，请调整吨位或跨度规则")

    def _rules_overlap(self, left, right):
        left_tonnage = self._rule_interval(left.tonnage_rule_type, left.tonnage_exact, left.tonnage_min, left.tonnage_max)
        right_tonnage = self._rule_interval(right.tonnage_rule_type, right.tonnage_exact, right.tonnage_min, right.tonnage_max)
        left_span = self._rule_interval(left.span_rule_type, left.span_exact, left.span_min, left.span_max)
        right_span = self._rule_interval(right.span_rule_type, right.span_exact, right.span_min, right.span_max)
        return self._intervals_overlap(left_tonnage, right_tonnage) and self._intervals_overlap(left_span, right_span)

    def _rule_interval(self, rule_type: str, exact: Any, minimum: Any, maximum: Any):
        if rule_type == "EXACT":
            parsed = self._parse_number(exact)
            return (parsed, parsed) if parsed is not None else None
        return minimum, maximum

    def _intervals_overlap(self, left: tuple[float, float] | None, right: tuple[float, float] | None):
        if left is None or right is None:
            return False
        return not (left[1] < right[0] or right[1] < left[0])

    def _next_version_number(self, group_id: int):
        latest = (
            self.db.query(EquipmentTemplateVersion)
            .filter(EquipmentTemplateVersion.group_id == group_id)
            .order_by(EquipmentTemplateVersion.version.desc(), EquipmentTemplateVersion.id.desc())
            .first()
        )
        return 1 if latest is None else latest.version + 1

    def _find_source_version(self, group_id: int | None, version_number: int | None):
        if not group_id or not version_number:
            return None
        return (
            self.db.query(EquipmentTemplateVersion)
            .filter(
                EquipmentTemplateVersion.group_id == group_id,
                EquipmentTemplateVersion.version == version_number,
            )
            .first()
        )

    def _build_candidate_snapshot(self, equipment: Equipment, source_version: EquipmentTemplateVersion | None):
        parts = [
            {"part_name": part.part_name, "specification": part.specification, "quantity": part.quantity}
            for part in self.db.query(EquipmentPart).filter(EquipmentPart.equipment_id == equipment.id).all()
        ]
        inspection_items = self._load_json(equipment.inspection_items_json, [])
        snapshot = {
            "category": equipment.category,
            "model_type": equipment.model_type,
            "group_name": f"{equipment.category}-{equipment.model_type} 模板组",
            "name": source_version.name if source_version else f"{equipment.category}-{equipment.model_type} 自动沉淀模板",
            "manufacturer": equipment.manufacturer,
            "default_params": {
                "tonnage": equipment.tonnage,
                "span": equipment.span,
                "lifting_height": equipment.lifting_height,
                "work_class": equipment.work_class,
                "installation_location": equipment.installation_location,
            },
            "parts": parts,
            "inspection_items": inspection_items,
            "version_note": "由设备录入候选沉淀生成",
            "base_template_id": source_version.base_template_id if source_version else None,
        }
        if source_version:
            snapshot.update(
                {
                    "tonnage_rule_type": source_version.tonnage_rule_type,
                    "tonnage_exact": source_version.tonnage_exact,
                    "tonnage_min": source_version.tonnage_min,
                    "tonnage_max": source_version.tonnage_max,
                    "span_rule_type": source_version.span_rule_type,
                    "span_exact": source_version.span_exact,
                    "span_min": source_version.span_min,
                    "span_max": source_version.span_max,
                }
            )
        else:
            snapshot.update(
                {
                    "tonnage_rule_type": "EXACT",
                    "tonnage_exact": equipment.tonnage,
                    "tonnage_min": None,
                    "tonnage_max": None,
                    "span_rule_type": "EXACT",
                    "span_exact": equipment.span,
                    "span_min": None,
                    "span_max": None,
                }
            )
        return snapshot

    def _build_diff_summary(self, source_version: EquipmentTemplateVersion | None, snapshot: dict[str, Any]):
        fields = ["default_params", "parts", "inspection_items"]
        if not source_version:
            return [{"field": field, "change_type": "NEW"} for field in fields]

        source = self.serialize_version(source_version)
        diff_summary = []
        for field in fields:
            if source.get(field) != snapshot.get(field):
                diff_summary.append(
                    {
                        "field": field,
                        "change_type": "MODIFIED",
                        "before_count": len(source.get(field, [])) if isinstance(source.get(field), list) else None,
                        "after_count": len(snapshot.get(field, [])) if isinstance(snapshot.get(field), list) else None,
                    }
                )
        return diff_summary

    def _find_or_create_group(self, category: str, model_type: str, name: str, user_id: int):
        group = (
            self.db.query(EquipmentTemplateGroup)
            .filter(
                EquipmentTemplateGroup.category == category,
                EquipmentTemplateGroup.model_type == model_type,
            )
            .first()
        )
        if group:
            return group
        group = EquipmentTemplateGroup(category=category, model_type=model_type, name=name, created_by=user_id)
        self.db.add(group)
        self.db.flush()
        return group

    def _match_rule(self, version: EquipmentTemplateVersion, tonnage: str | None, span: str | None):
        return self._match_single_rule(version.tonnage_rule_type, version.tonnage_exact, version.tonnage_min, version.tonnage_max, tonnage) and self._match_single_rule(
            version.span_rule_type, version.span_exact, version.span_min, version.span_max, span
        )

    def _match_single_rule(self, rule_type: str, exact: Any, minimum: Any, maximum: Any, value: Any):
        if value in (None, ""):
            return True
        if rule_type == "EXACT":
            parsed_value = self._parse_number(value)
            parsed_exact = self._parse_number(exact)
            if parsed_value is not None and parsed_exact is not None:
                return abs(parsed_value - parsed_exact) < 1e-6
            return self._normalize_text(value) == self._normalize_text(exact)
        parsed_value = self._parse_number(value)
        if parsed_value is None:
            return False
        return minimum <= parsed_value <= maximum

    def _is_range_rule(self, version: EquipmentTemplateVersion):
        return version.tonnage_rule_type == "RANGE" or version.span_rule_type == "RANGE"

    def _is_exact_rule(self, payload):
        return payload.tonnage_rule_type == "EXACT" and payload.span_rule_type == "EXACT"

    def _is_exact_supplement_pair(self, left, right):
        left_exact = self._is_exact_rule(left)
        right_exact = self._is_exact_rule(right)
        return (left_exact and self._is_range_rule(right)) or (right_exact and self._is_range_rule(left))

    def _parse_number(self, value: Any) -> Optional[float]:
        if value in (None, ""):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"-?\d+(?:\.\d+)?", str(value))
        return float(match.group(0)) if match else None

    def _normalize_manufacturer(self, manufacturer: str | None):
        if manufacturer is None:
            return None
        manufacturer = manufacturer.strip()
        return manufacturer or None

    def _normalize_text(self, value: Any):
        return "" if value is None else str(value).strip().lower()

    def _load_json(self, raw: str | None, default):
        if not raw:
            return default
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return default

    def _dict_as_rule_payload(self, payload: dict[str, Any]):
        class RulePayload:
            manufacturer = payload.get("manufacturer")
            tonnage_rule_type = payload["tonnage_rule_type"]
            tonnage_exact = payload.get("tonnage_exact")
            tonnage_min = payload.get("tonnage_min")
            tonnage_max = payload.get("tonnage_max")
            span_rule_type = payload["span_rule_type"]
            span_exact = payload.get("span_exact")
            span_min = payload.get("span_min")
            span_max = payload.get("span_max")

        return RulePayload
