from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from main import app
from models.customer import Customer
from models.equipment import Equipment
from models.repair_order import RepairOrder
from models.user import RoleEnum, User
from models.work_order import InspectionItem, OrderStatus, WorkOrder
from services import pdf_service


def _build_session_factory(tmp_path: Path):
    db_path = tmp_path / "pdf-report-test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def _seed_records(session):
    customer = Customer(
        company_name="测试客户有限公司",
        contact_name="张经理",
        contact_phone="13800138000",
        address="上海市浦东新区测试路 88 号",
        login_phone="13800138000",
    )
    session.add(customer)
    session.flush()

    equipment = Equipment(
        customer_id=customer.id,
        name="桥式起重机 A01",
        model_type="QD10T-28.5M",
        category="桥式起重机",
        tonnage="10T",
        span="28.5M",
        lifting_height="12M",
        work_class="A5",
        installation_location="一号厂房东侧",
    )
    session.add(equipment)

    technician = User(
        username="pdf-tech",
        password_hash="not-used",
        role=RoleEnum.TECH,
        name="王工",
        phone="13900139000",
    )
    session.add(technician)
    session.flush()

    work_order = WorkOrder(
        order_type="月检",
        customer_id=customer.id,
        equipment_id=equipment.id,
        technician_id=technician.id,
        plan_date=date(2026, 3, 18),
        status=OrderStatus.COMPLETED,
        problem_description="制动器运行正常，钢丝绳无明显磨损。",
        solution="完成常规润滑与紧固复核。",
        sign_url="",
        updated_at=datetime(2026, 3, 18, 10, 0, 0),
    )
    session.add(work_order)
    session.flush()

    session.add(
        InspectionItem(
            work_order_id=work_order.id,
            item_name="制动器检查",
            result="NORMAL",
            comment="制动间隙正常",
        )
    )

    repair_order = RepairOrder(
        equipment_id=equipment.id,
        tech_id=technician.id,
        fault_symptom="大车运行有异响",
        fault_component="减速机",
        fault_cause="润滑不足",
        site_photos=[],
        parts_used=[{"name": "润滑脂", "quantity": 2, "unit": "桶"}],
        labor_fee=300,
        other_fee=80,
        total_fee=380,
        is_warranty=False,
        prevention_advice="建议下月复检减速机油位",
        client_sign_url="",
        fee_confirmed=True,
        status="已完成",
        completed_at=datetime(2026, 3, 18, 11, 0, 0),
    )
    session.add(repair_order)
    session.commit()
    return work_order.id, repair_order.id


def test_generate_maintenance_and_repair_reports(tmp_path, monkeypatch):
    session_factory = _build_session_factory(tmp_path)
    session = session_factory()
    work_order_id, repair_order_id = _seed_records(session)
    session.close()

    monkeypatch.setattr("core.database.SessionLocal", session_factory)
    monkeypatch.setattr(
        pdf_service,
        "upload_bytes",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("skip upload")),
    )

    pdf_service.generate_maintenance_report(work_order_id)
    pdf_service.generate_repair_report(repair_order_id)

    verify_session = session_factory()
    work_order = verify_session.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    repair_order = verify_session.query(RepairOrder).filter(RepairOrder.id == repair_order_id).first()
    verify_session.close()

    assert work_order is not None
    assert repair_order is not None
    assert work_order.pdf_report_url == f"/uploads/reports/work_order_{work_order_id}.pdf"
    assert repair_order.pdf_report_url == f"/uploads/reports/repair_order_{repair_order_id}.pdf"

    work_order_pdf = Path("uploads/reports") / f"work_order_{work_order_id}.pdf"
    repair_order_pdf = Path("uploads/reports") / f"repair_order_{repair_order_id}.pdf"
    assert work_order_pdf.exists()
    assert repair_order_pdf.exists()
    assert work_order_pdf.stat().st_size > 0
    assert repair_order_pdf.stat().st_size > 0

    client = TestClient(app)
    maintenance_download = client.get(f"/uploads/reports/work_order_{work_order_id}.pdf")
    repair_download = client.get(f"/uploads/reports/repair_order_{repair_order_id}.pdf")

    assert maintenance_download.status_code == 200
    assert repair_download.status_code == 200
    assert maintenance_download.headers["content-type"] == "application/pdf"
    assert repair_download.headers["content-type"] == "application/pdf"

    work_order_pdf.unlink(missing_ok=True)
    repair_order_pdf.unlink(missing_ok=True)
