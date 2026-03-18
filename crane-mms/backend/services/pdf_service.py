import io
import logging
import os
from datetime import datetime
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xhtml2pdf import pisa

from models.repair_order import RepairOrder
from models.work_order import WorkOrder
from services.cos_service import upload_bytes

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
UPLOAD_DIR = BASE_DIR / "uploads" / "reports"

# 注册中文字体 (微软雅黑)
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
try:
    if os.path.exists(FONT_PATH):
        # 注册字体，subfontIndex=0 表示 TTC 中的第一个字体
        pdfmetrics.registerFont(TTFont('YaHei', FONT_PATH, subfontIndex=0))
        logger.info(f"Successfully registered font YaHei from {FONT_PATH}")
    else:
        logger.warning(f"Font file not found: {FONT_PATH}")
except Exception as e:
    logger.error(f"Failed to register font: {e}")

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    # handle fonts
    if uri == "msyh.ttc" or uri.endswith("msyh.ttc"):
        return FONT_PATH
        
    # handle images and other resources
    if not uri.startswith('http'):
        path = BASE_DIR / uri.lstrip("/").replace("/", os.sep)
        if path.exists():
            return str(path)
            
    return uri

def fetch_image_local(url, temp_dir="uploads/tmp"):
    if not url: return None
    if url.startswith("data:"):
        return None
    if url.startswith("/"):
        local_path = BASE_DIR / url.lstrip("/")
        if local_path.exists():
            return str(local_path)
        return url
        
    try:
        temp_path = BASE_DIR / temp_dir
        temp_path.mkdir(parents=True, exist_ok=True)
        filename = temp_path / os.path.basename(url.split("?")[0])
        if not filename.exists():
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(res.content)
            else:
                return url
        return str(filename.resolve())
    except Exception as e:
        logger.error(f"Failed to fetch image {url}: {e}")
        return url


def _build_template_env():
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def _create_pdf_bytes(html_content: str) -> bytes | None:
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        io.StringIO(html_content),
        dest=pdf_file,
        encoding="utf-8",
        link_callback=link_callback,
    )
    if pisa_status.err:
        logger.error("PDF generation error")
        return None
    return pdf_file.getvalue()


def _persist_pdf(pdf_bytes: bytes, filename: str) -> str:
    try:
        return upload_bytes(pdf_bytes, filename, "application/pdf")
    except Exception:
        local_path = BASE_DIR / "uploads" / filename
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as file:
            file.write(pdf_bytes)
        return f"/uploads/{filename.replace(os.sep, '/')}"


def _repair_status_label(status: str | None) -> str:
    status_map = {
        "PENDING": "待处理",
        "IN_PROGRESS": "进行中",
        "PENDING_SIGN": "待客户确认",
        "COMPLETED": "已完成",
        "待处理": "待处理",
        "进行中": "进行中",
        "待客户确认": "待客户确认",
        "已完成": "已完成",
    }
    return status_map.get(status or "", status or "未设置")

def generate_maintenance_report(order_id: int):
    from core.database import SessionLocal
    db = SessionLocal()
    try:
        order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
        if not order: 
            return
            
        env = _build_template_env()
        template = env.get_template("report.html")
        
        sign_img_local = fetch_image_local(order.sign_url) if order.sign_url else None
        
        html_content = template.render(
            order=order,
            customer=order.customer,
            equipment=order.equipment,
            items=order.inspection_items,
            sign_img_local=sign_img_local
        )
        
        pdf_bytes = _create_pdf_bytes(html_content)
        if not pdf_bytes:
            return

        filename = f"reports/work_order_{order.id}.pdf"
        pdf_url = _persist_pdf(pdf_bytes, filename)
            
        order.pdf_report_url = pdf_url
        db.commit()
        logger.info(f"Report generated successfully: {pdf_url}")
    except Exception as e:
        import traceback
        logger.error(f"Error generating PDF: {traceback.format_exc()}")
    finally:
        db.close()


def generate_repair_report(repair_id: int):
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        repair = db.query(RepairOrder).filter(RepairOrder.id == repair_id).first()
        if not repair:
            return

        equipment = repair.equipment
        customer = equipment.customer if equipment else None
        technician = repair.tech

        env = _build_template_env()
        template = env.get_template("report_repair.html")

        site_photo_locals = [
            fetch_image_local(photo)
            for photo in (repair.site_photos or [])
            if photo
        ]
        sign_img_local = fetch_image_local(repair.client_sign_url) if repair.client_sign_url else None
        parts_used = repair.parts_used or []

        html_content = template.render(
            repair=repair,
            equipment=equipment,
            customer=customer,
            technician=technician,
            site_photo_locals=site_photo_locals,
            parts_used=parts_used,
            status_label=_repair_status_label(repair.status),
            generated_at=(repair.completed_at or repair.created_at or datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S"),
            sign_img_local=sign_img_local,
        )

        pdf_bytes = _create_pdf_bytes(html_content)
        if not pdf_bytes:
            return

        filename = f"reports/repair_order_{repair.id}.pdf"
        pdf_url = _persist_pdf(pdf_bytes, filename)
        repair.pdf_report_url = pdf_url
        db.commit()
        logger.info(f"Repair report generated successfully: {pdf_url}")
    except Exception:
        import traceback

        logger.error(f"Error generating repair PDF: {traceback.format_exc()}")
    finally:
        db.close()
