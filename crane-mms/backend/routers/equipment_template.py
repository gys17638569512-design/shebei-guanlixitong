from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.permissions import get_current_user, require_permission
from core.response import ok
from models.user import User
from schemas.equipment_template import (
    CandidateReviewRequest,
    EquipmentTemplateCandidateCreate,
    EquipmentTemplateGroupCreate,
    EquipmentTemplateVersionSave,
    InspectionBaseTemplateSave,
)
from services.equipment_template_service import EquipmentTemplateService

router = APIRouter(prefix="", tags=["设备模板中心"])


@router.get("/equipment-template-groups", summary="获取设备模板组列表")
def list_groups(
    category: str | None = Query(None),
    model_type: str | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_permission("settings.equipment_templates.access")),
):
    return ok(EquipmentTemplateService(db).list_groups(category=category, model_type=model_type))


@router.post("/equipment-template-groups", summary="创建设备模板组")
def create_group(
    payload: EquipmentTemplateGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.group.manage")),
):
    return ok(EquipmentTemplateService(db).create_group(payload, current_user.id))


@router.get("/equipment-template-versions/{version_id}", summary="获取模板版本详情")
def get_version(
    version_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_permission("settings.equipment_templates.access")),
):
    return ok(EquipmentTemplateService(db).get_version(version_id))


@router.post("/equipment-template-versions", summary="创建模板版本")
def create_version(
    payload: EquipmentTemplateVersionSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.version.manage")),
):
    return ok(EquipmentTemplateService(db).create_version(payload, current_user.id))


@router.put("/equipment-template-versions/{version_id}", summary="更新模板版本并生成新版本")
def update_version(
    version_id: int,
    payload: EquipmentTemplateVersionSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.version.manage")),
):
    return ok(EquipmentTemplateService(db).update_version(version_id, payload, current_user.id))


@router.get("/equipment-template-match", summary="按设备参数匹配模板")
def match_template(
    category: str = Query(...),
    model_type: str = Query(...),
    tonnage: str | None = Query(None),
    span: str | None = Query(None),
    manufacturer: str | None = Query(None),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return ok(EquipmentTemplateService(db).match_template(category, model_type, tonnage, span, manufacturer))


@router.get("/equipment-template-candidates", summary="获取模板候选列表")
def list_candidates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.module.candidates")),
):
    return ok(EquipmentTemplateService(db).list_candidates())


@router.post("/equipment-template-candidates", summary="手动创建模板候选")
def create_candidate(
    payload: EquipmentTemplateCandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(EquipmentTemplateService(db).create_candidate(payload, current_user.id))


@router.post("/equipment-template-candidates/{candidate_id}/approve", summary="通过模板候选并生成新版本")
def approve_candidate(
    candidate_id: int,
    payload: CandidateReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.candidates.review")),
):
    return ok(EquipmentTemplateService(db).approve_candidate(candidate_id, current_user.id, payload.review_note))


@router.post("/equipment-template-candidates/{candidate_id}/reject", summary="驳回模板候选")
def reject_candidate(
    candidate_id: int,
    payload: CandidateReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.candidates.review")),
):
    return ok(EquipmentTemplateService(db).reject_candidate(candidate_id, payload.review_note))


@router.get("/inspection-base-templates", summary="获取检修通用模板列表")
def list_base_templates(
    category: str | None = Query(None),
    model_type: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.module.base_templates")),
):
    return ok(EquipmentTemplateService(db).list_base_templates(category=category, model_type=model_type))


@router.post("/inspection-base-templates", summary="创建检修通用模板")
def create_base_template(
    payload: InspectionBaseTemplateSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.base_template.manage")),
):
    return ok(EquipmentTemplateService(db).create_base_template(payload, current_user.id))


@router.put("/inspection-base-templates/{template_id}", summary="更新检修通用模板")
def update_base_template(
    template_id: int,
    payload: InspectionBaseTemplateSave,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings.equipment_templates.base_template.manage")),
):
    return ok(EquipmentTemplateService(db).update_base_template(template_id, payload))
