from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings

# engine = create_engine(settings.DATABASE_URL)

def _make_engine(url: str):
    # SQLite 用于测试，不需要连接池配置
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    # MySQL 生产配置
    return create_engine(
        url,
        pool_pre_ping=True,      # 每次使用前检测连接是否存活
        pool_size=10,            # 连接池大小
        max_overflow=20,         # 超出 pool_size 后最多额外创建数量
        pool_recycle=3600,       # 连接存活 1 小时后强制回收，防止 MySQL 超时断开
        pool_timeout=30,         # 等待连接超时时间（秒）
    )

engine = _make_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()