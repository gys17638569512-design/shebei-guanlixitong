from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from core.settings import settings
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)


def upload_file(local_path: str, cos_key: str) -> str:
    """上传文件到COS，返回公开访问URL"""
    try:
        # 检查COS配置
        if not all([settings.COS_SECRET_ID, settings.COS_SECRET_KEY, settings.COS_BUCKET]):
            # 如果没有配置COS，返回本地路径作为fallback
            return local_path
        
        # 初始化COS客户端
        config = CosConfig(
            Region=settings.COS_REGION,
            SecretId=settings.COS_SECRET_ID,
            SecretKey=settings.COS_SECRET_KEY
        )
        client = CosS3Client(config)
        
        # 上传文件
        response = client.upload_file(
            Bucket=settings.COS_BUCKET,
            LocalFilePath=local_path,
            Key=cos_key,
            PartSize=1024 * 1024 * 5,
            MAXThread=10,
            EnableMD5=False
        )
        
        # 生成公开访问URL
        url = f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{cos_key}"
        return url
    except Exception as e:
        logging.error(f"COS上传失败: {e}")
        # 失败时返回本地路径
        return local_path


def upload_bytes(data: bytes, cos_key: str, content_type: str) -> str:
    """上传字节流到COS，返回公开访问URL"""
    try:
        # 检查COS配置
        if not all([settings.COS_SECRET_ID, settings.COS_SECRET_KEY, settings.COS_BUCKET]):
            # 如果没有配置COS，保存到本地并返回路径
            if not os.path.exists(os.path.dirname(f"uploads/{cos_key}")):
                os.makedirs(os.path.dirname(f"uploads/{cos_key}"), exist_ok=True)
            local_path = f"uploads/{cos_key}"
            with open(local_path, "wb") as f:
                f.write(data)
            return local_path
        
        # 初始化COS客户端
        config = CosConfig(
            Region=settings.COS_REGION,
            SecretId=settings.COS_SECRET_ID,
            SecretKey=settings.COS_SECRET_KEY
        )
        client = CosS3Client(config)
        
        # 上传字节流
        response = client.put_object(
            Bucket=settings.COS_BUCKET,
            Key=cos_key,
            Body=data,
            ContentType=content_type
        )
        
        # 生成公开访问URL
        url = f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{cos_key}"
        return url
    except Exception as e:
        logging.error(f"COS上传失败: {e}")
        # 失败时保存到本地
        if not os.path.exists(os.path.dirname(f"uploads/{cos_key}")):
            os.makedirs(os.path.dirname(f"uploads/{cos_key}"), exist_ok=True)
        local_path = f"uploads/{cos_key}"
        with open(local_path, "wb") as f:
            f.write(data)
        return local_path