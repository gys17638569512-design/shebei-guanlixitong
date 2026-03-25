from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.security import create_access_token
from main import app
from models.customer import Customer
from models.equipment import Equipment
from models.user import RoleEnum, User
from models.work_order import OrderStatus, WorkOrder


def _build_session_factory(tmp_path: Path):
    db_path = tmp_path / "report-archive.db"
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


def _seed_archive_orders(session_factory):
    session = session_factory()

    admin = User(
        username="report-admin",
        password_hash="not-used",
        role=RoleEnum.ADMIN,
        name="报告管理员",
        phone="13800138000",
    )
    tech = User(
        username="report-tech",
        password_hash="not-used",
        role=RoleEnum.TECH,
        name="测试工程师",
        phone="13900139000",
    )
    customer = Customer(
        company_name="报告归档测试客户",
        contact_name="王主管",
        contact_phone="13700137000",
        address="上海市归档路 66 号",
        login_phone="13700137000",
    )
    session.add_all([admin, tech, customer])
    session.flush()

    equipment = Equipment(
        customer_id=customer.id,
        name="QD-32/5t 桥式起重机",
        model_type="QD",
        category="桥式起重机",
        manufacturer="沪工",
        tonnage="32/5t",
        span="22.5m",
        lifting_height="12m",
        work_class="A5",
        installation_location="一号车间",
    )
    session.add(equipment)
    session.flush()

    older_order = WorkOrder(
        order_type="月检",
        customer_id=customer.id,
        equipment_id=equipment.id,
        technician_id=tech.id,
        plan_date=date(2026, 3, 20),
        status=OrderStatus.COMPLETED,
        pdf_report_url="/uploads/reports/work_order_1.pdf",
        esign_cert_url="/uploads/certs/work_order_1.pdf",
        updated_at=datetime(2026, 3, 20, 9, 30, 0),
    )
    newer_order = WorkOrder(
        order_type="季检",
        customer_id=customer.id,
        equipment_id=equipment.id,
        technician_id=tech.id,
        plan_date=date(2026, 3, 21),
        status=OrderStatus.COMPLETED,
        pdf_report_url="/uploads/reports/work_order_2.pdf",
        esign_cert_url="/uploads/certs/work_order_2.pdf",
        updated_at=datetime(2026, 3, 21, 18, 45, 0),
    )
    session.add_all([older_order, newer_order])
    session.commit()
    session.refresh(admin)
    session.refresh(older_order)
    session.refresh(newer_order)
    session.close()

    return admin, older_order, newer_order


def test_report_archive_returns_orders_sorted_by_archive_time(monkeypatch, tmp_path):
    session_factory = _build_session_factory(tmp_path)
    monkeypatch.setattr("core.database.SessionLocal", session_factory)

    admin, older_order, newer_order = _seed_archive_orders(session_factory)
    client = TestClient(app)

    response = client.get("/api/v1/orders/reports/archive", headers=_auth_header(admin))

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 200, body
    assert [item["order_id"] for item in body["data"]] == [newer_order.id, older_order.id]
    assert body["data"][0]["completed_at"] == "2026-03-21 18:45:00"
    assert body["data"][1]["completed_at"] == "2026-03-20 09:30:00"
