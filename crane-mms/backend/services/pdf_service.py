import os
import io
import requests
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
from sqlalchemy.orm import Session
from models.work_order import WorkOrder
from services.cos_service import upload_bytes
import logging
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

logger = logging.getLogger(__name__)

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
        # Local paths
        path = os.path.join(os.getcwd(), uri.replace('/', os.sep))
        if os.path.exists(path):
            return path
            
    return uri

def fetch_image_local(url, temp_dir="uploads/tmp"):
    if not url: return None
    if url.startswith("data:"):
        return None
    if url.startswith("/"):
        local_path = url.lstrip("/")
        if os.path.exists(local_path):
            return os.path.abspath(local_path)
        return url
        
    try:
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        filename = os.path.join(temp_dir, os.path.basename(url.split("?")[0]))
        if not os.path.exists(filename):
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(res.content)
            else:
                return url
        return os.path.abspath(filename)
    except Exception as e:
        logger.error(f"Failed to fetch image {url}: {e}")
        return url

def generate_maintenance_report(order_id: int):
    from core.database import SessionLocal
    db = SessionLocal()
    try:
        order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
        if not order: 
            return
            
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("report.html")
        
        sign_img_local = fetch_image_local(order.sign_url) if order.sign_url else None
        
        html_content = template.render(
            order=order,
            customer=order.customer,
            equipment=order.equipment,
            items=order.inspection_items,
            sign_img_local=sign_img_local
        )
        
        pdf_file = io.BytesIO()
        # Use link_callback to resolve paths
        pisa_status = pisa.CreatePDF(
            io.StringIO(html_content), 
            dest=pdf_file, 
            encoding='utf-8',
            link_callback=link_callback
        )
        
        if pisa_status.err:
            logger.error(f"PDF generation error for order {order_id}")
            return
            
        pdf_bytes = pdf_file.getvalue()
        
        filename = f"reports/work_order_{order.id}.pdf"
        try:
            pdf_url = upload_bytes(pdf_bytes, filename, "application/pdf")
        except Exception as e:
            local_path = f"uploads/reports/work_order_{order.id}.pdf"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                 f.write(pdf_bytes)
            pdf_url = f"/{local_path}"
            
        order.pdf_report_url = pdf_url
        db.commit()
        logger.info(f"Report generated successfully: {pdf_url}")
    except Exception as e:
        import traceback
        logger.error(f"Error generating PDF: {traceback.format_exc()}")
    finally:
        db.close()
