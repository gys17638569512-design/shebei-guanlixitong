from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from models.work_order import WorkOrder, InspectionItem
from core.database import get_db
from services.cos_service import upload_bytes
import base64
import requests
import os
from datetime import datetime


def generate_maintenance_report(order_id: int, db) -> str:
    """生成维保报告并上传到COS"""
    try:
        # 查询工单数据
        order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
        if not order:
            raise Exception("工单不存在")
        
        # 查询检查项目
        inspection_items = db.query(InspectionItem).filter(InspectionItem.work_order_id == order_id).all()
        
        # 准备数据
        report_data = {
            "report_number": f"CRANE-{order_id}-{datetime.now().strftime('%Y%m%d')}",
            "generate_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "company_name": order.customer.company_name,
            "equipment": {
                "name": order.equipment.name,
                "model_type": order.equipment.model_type,
                "installation_location": order.equipment.installation_location
            },
            "customer": {
                "company_name": order.customer.company_name,
                "contact_name": order.customer.contact_name,
                "contact_phone": order.customer.contact_phone
            },
            "technician": order.technician.name,
            "inspection_items": [],
            "photos": [],
            "signature": "",
            "checkin_info": {
                "time": order.checkin_time.strftime("%Y-%m-%d %H:%M:%S") if order.checkin_time else "",
                "address": order.checkin_address or ""
            }
        }
        
        # 处理检查项目
        for item in inspection_items:
            report_data["inspection_items"].append({
                "item_name": item.item_name,
                "result": "正常" if item.result == "NORMAL" else "异常",
                "result_icon": "✓" if item.result == "NORMAL" else "✗",
                "comment": item.comment or ""
            })
        
        # 处理照片
        if order.photo_urls:
            import json
            try:
                photo_urls = json.loads(order.photo_urls)
                for i, url in enumerate(photo_urls[:6]):  # 最多6张
                    try:
                        # 下载照片并转为base64
                        response = requests.get(url)
                        if response.status_code == 200:
                            img_base64 = base64.b64encode(response.content).decode('utf-8')
                            report_data["photos"].append(f"data:image/jpeg;base64,{img_base64}")
                        else:
                            # 照片下载失败，使用占位图
                            report_data["photos"].append("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='150' viewBox='0 0 200 150'%3E%3Crect width='200' height='150' fill='%23f0f0f0'/%3E%3Ctext x='100' y='80' font-family='Arial' font-size='14' text-anchor='middle' fill='%23999'%3E照片加载失败%3C/text%3E%3C/svg%3E")
                    except Exception:
                        # 异常时使用占位图
                        report_data["photos"].append("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='150' viewBox='0 0 200 150'%3E%3Crect width='200' height='150' fill='%23f0f0f0'/%3E%3Ctext x='100' y='80' font-family='Arial' font-size='14' text-anchor='middle' fill='%23999'%3E照片加载失败%3C/text%3E%3C/svg%3E")
            except json.JSONDecodeError:
                pass
        
        # 处理签名
        if order.sign_url:
            try:
                response = requests.get(order.sign_url)
                if response.status_code == 200:
                    sign_base64 = base64.b64encode(response.content).decode('utf-8')
                    report_data["signature"] = f"data:image/png;base64,{sign_base64}"
            except Exception:
                pass
        
        # 加载Jinja2模板
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('report_maintenance.html')
        
        # 渲染HTML
        html_content = template.render(**report_data)
        
        # 生成PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        # 上传到COS
        pdf_key = f"reports/maintenance_report_{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf_url = upload_bytes(pdf_bytes, pdf_key, "application/pdf")
        
        # 更新数据库
        order.pdf_report_url = pdf_url
        db.commit()
        
        return pdf_url
    except Exception as e:
        print(f"PDF生成失败: {e}")
        # 生成失败时返回空
        return ""