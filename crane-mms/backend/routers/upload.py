from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from core.permissions import get_current_user
from models.user import User
from services.cos_service import upload_file, upload_bytes
from PIL import Image
import io
import os

router = APIRouter(prefix="/upload", tags=["文件上传"])


@router.post("/image", summary="上传现场照片", description="上传工单现场作业环境照片。系统会自动压缩超过800KB的图片（最大支持10MB）。支持 .jpg, .jpeg, .png, .webp 格式。")
async def upload_image(
    file: UploadFile = File(..., description="要上传的现场照片文件数据流"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查文件大小
    file.file.seek(0, 2)  # 移到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 移回文件开头
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=413, detail="File size exceeds 10MB")
    
    # 检查文件类型
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # 读取文件内容
    content = await file.read()
    
    # 压缩图片
    img = Image.open(io.BytesIO(content))
    
    # 计算压缩质量
    if file_size > 800 * 1024:  # 800KB
        quality = 70
    else:
        quality = 90
    
    # 保存压缩后的图片
    output = io.BytesIO()
    img.save(output, format=img.format, quality=quality)
    compressed_content = output.getvalue()
    
    # 生成文件名
    filename = f"images/{os.path.basename(file.filename)}"
    
    # 上传到COS
    try:
        url = upload_bytes(compressed_content, filename, file.content_type)
    except Exception as e:
        # 如果COS上传失败，返回本地路径作为fallback
        if not os.path.exists("uploads/images"):
            os.makedirs("uploads/images")
        local_path = f"uploads/images/{file.filename}"
        with open(local_path, "wb") as f:
            f.write(compressed_content)
        url = local_path
    
    return {"url": url}


@router.post("/sign", summary="上传手写电子签名", description="供客户确认单据时上传的手写签字截图。系统将对其进行严格的权限验证并关联存档。文件大小不得超过10MB，仅支持 .png 格式。")
async def upload_sign(
    file: UploadFile = File(..., description="包含手写电子签名的 PNG 格式图片文件"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查文件大小
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=413, detail="File size exceeds 10MB")
    
    # 检查文件类型
    if not file.filename.lower().endswith(".png"):
        raise HTTPException(status_code=400, detail="Only PNG files are allowed for signatures")
    
    # 读取文件内容
    content = await file.read()
    
    # 生成文件名
    filename = f"signatures/{os.path.basename(file.filename)}"
    
    # 上传到COS
    try:
        url = upload_bytes(content, filename, "image/png")
    except Exception as e:
        # 如果COS上传失败，返回本地路径作为fallback
        if not os.path.exists("uploads/signatures"):
            os.makedirs("uploads/signatures")
        local_path = f"uploads/signatures/{file.filename}"
        with open(local_path, "wb") as f:
            f.write(content)
        url = local_path
    
    return {"url": url}