from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.security import create_access_token
from main import app
from models.audit_log import AuditLog
from models.customer import Customer
from models.equipment import Equipment
from models.repair_order import RepairOrder
from models.user import RoleEnum, User
from models.work_order import InspectionItem, OrderStatus, WorkOrder


def _build_session_factory(tmp_path: Path):
    db_path = tmp_path / "stats-workbench.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return testing_session_local


def _auth_header(user: User):
    token = create_access_token({"sub": user.username})
    return {"Authorization": f"Bearer {token}"}


def _seed_workbench_data(session_factory):
    session = session_factory()
    today = date.today()

    manager = User(
        username="workbench-manager",
        password_hash="not-used",
        role=RoleEnum.MANAGER,
        name="工作台经理",
        phone="13800138000",
    )
    tech = User(
        username="workbench-tech",
        password_hash="not-used",
        role=RoleEnum.TECH,
        name="现场工程师",
        phone="13900139000",
    )
    session.add_all([manager, tech])
    session.flush()

    customer_a = Customer(
        company_name="华东重工",
        contact_name="李厂长",
        contact_phone="13700137000",
        address="上海市浦东新区临港大道 8 号",
        login_phone="13700137000",
    )
    customer_b = Customer(
        company_name="江南制造",
        contact_name="周主任",
        contact_phone="13600136000",
        address="苏州市工业园区 66 号",
        login_phone="13600136000",
    )
    session.add_all([customer_a, customer_b])
    session.flush()

    overdue_equipment = Equipment(
        customer_id=customer_a.id,
        name="A1 双梁桥机",
        model_type="QD",
        category="桥式起重机",
        manufacturer="沪工",
        tonnage="20t",
        span="22.5m",
        lifting_height="12m",
        work_class="A5",
        installation_location="一号厂房",
        next_inspection_date=today - timedelta(days=5),
    )
    warning_equipment = Equipment(
        customer_id=customer_a.id,
        name="A2 单梁桥机",
        model_type="LD",
        category="桥式起重机",
        manufacturer="卫华",
        tonnage="10t",
        span="16.5m",
        lifting_height="9m",
        work_class="A3",
        installation_location="二号厂房",
        next_inspection_date=today + timedelta(days=10),
    )
    safe_equipment = Equipment(
        customer_id=customer_b.id,
        name="B1 门机",
        model_type="MG",
        category="门式起重机",
        manufacturer="太重",
        tonnage="32t",
        span="28m",
        lifting_height="10m",
        work_class="A5",
        installation_location="成品堆场",
        next_inspection_date=today + timedelta(days=120),
    )
    session.add_all([overdue_equipment, warning_equipment, safe_equipment])
    session.flush()

    pending_order = WorkOrder(
        order_type="月检",
        customer_id=customer_a.id,
        equipment_id=overdue_equipment.id,
        technician_id=tech.id,
        plan_date=today,
        status=OrderStatus.PENDING,
        created_at=datetime(2026, 3, 25, 8, 0, 0),
    )
    in_progress_order = WorkOrder(
        order_type="季检",
        customer_id=customer_a.id,
        equipment_id=warning_equipment.id,
        technician_id=tech.id,
        plan_date=today,
        status=OrderStatus.IN_PROGRESS,
        created_at=datetime(2026, 3, 25, 9, 0, 0),
    )
    pending_sign_order = WorkOrder(
        order_type="年检",
        customer_id=customer_b.id,
        equipment_id=safe_equipment.id,
        technician_id=tech.id,
        plan_date=today,
        status=OrderStatus.PENDING_SIGN,
        created_at=datetime(2026, 3, 25, 10, 0, 0),
    )
    completed_order = WorkOrder(
        order_type="月检",
        customer_id=customer_b.id,
        equipment_id=safe_equipment.id,
        technician_id=tech.id,
        plan_date=today,
        status=OrderStatus.COMPLETED,
        created_at=datetime(2026, 3, 25, 11, 0, 0),
    )
    session.add_all([pending_order, in_progress_order, pending_sign_order, completed_order])
    session.flush()

    session.add(
        InspectionItem(
            work_order_id=completed_order.id,
            item_name="制动器磨损",
            result="ABNORMAL",
            comment="制动衬垫磨损明显，需持续跟进",
        )
    )

    high_risk_repair = RepairOrder(
        equipment_id=overdue_equipment.id,
        tech_id=tech.id,
        fault_symptom="主梁异响并伴随制动失灵，现场已紧急停机",
        fault_component="制动器",
        fault_cause="高危隐患",
        status="进行中",
    )
    session.add(high_risk_repair)
    session.flush()

    session.add_all(
        [
            AuditLog(
                user_id=manager.id,
                action="UPDATE",
                table_name="equipments",
                record_id=overdue_equipment.id,
                new_value='{"next_inspection_date":"overdue"}',
                created_at=datetime.combine(today, datetime.min.time()).replace(hour=12, minute=0, second=0),
            ),
            AuditLog(
                user_id=manager.id,
                action="CREATE",
                table_name="work_orders",
                record_id=pending_order.id,
                new_value='{"status":"PENDING"}',
                created_at=datetime.combine(today, datetime.min.time()).replace(hour=12, minute=30, second=0),
            ),
        ]
    )

    session.commit()
    session.refresh(manager)
    session.refresh(tech)
    session.close()
    return manager, tech


def test_workbench_stats_returns_expected_management_payload(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    manager, _tech = _seed_workbench_data(session_factory)
    client = TestClient(app)

    response = client.get("/api/v1/stats/workbench", headers=_auth_header(manager))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 200, body

    data = body["data"]
    assert set(data.keys()) == {
        "alerts",
        "todos",
        "metrics",
        "schedule",
        "quick_actions",
        "recent_audits",
        "warning_summary",
    }

    assert data["metrics"] == {
        "today_order_count": 4,
        "in_progress_order_count": 2,
        "completed_order_count": 1,
        "equipment_total": 3,
        "customer_total": 2,
        "warning_equipment_count": 2,
    }

    assert data["warning_summary"] == {
        "overdue_inspection_count": 1,
        "inspection_due_soon_count": 1,
        "high_risk_order_count": 1,
    }

    assert data["alerts"]["overdue_equipments"][0]["equipment_name"] == "A1 双梁桥机"
    assert data["alerts"]["high_risk_orders"][0]["fault_component"] == "制动器"
    assert data["todos"]["pending_dispatch"][0]["status"] == "PENDING"
    assert data["todos"]["pending_report_confirmation"][0]["status"] == "PENDING_SIGN"
    assert data["todos"]["abnormal_follow_ups"][0]["inspection_result"] == "ABNORMAL"
    assert data["todos"]["approvals"] == []

    assert data["schedule"]["date"] == str(date.today())
    assert len(data["schedule"]["today_orders"]) == 4
    assert data["quick_actions"][0]["key"]
    assert len(data["recent_audits"]) == 2
    assert data["recent_audits"][0]["created_at"].endswith("12:30:00")


def test_workbench_stats_is_forbidden_for_tech_users(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    _manager, tech = _seed_workbench_data(session_factory)
    client = TestClient(app)

    response = client.get("/api/v1/stats/workbench", headers=_auth_header(tech))

    assert response.status_code == 403
