from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
import os

# 创建必要的数据目录
os.makedirs("data/database", exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # 调试模式下显示SQL语句
)

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def get_db() -> Session:
    """
    获取数据库会话依赖项
    
    Yields:
        Session: SQLAlchemy数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    初始化数据库，创建所有表
    
    Raises:
        Exception: 如果数据库初始化失败
    """
    try:
        # 导入所有模型以确保它们被注册
        from app.models.user import User
        from app.models.memory import Memory
        from app.models.message import Message
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功")
        
        # 如果是SQLite，设置WAL模式以获得更好的并发性能
        if "sqlite" in settings.DATABASE_URL:
            try:
                with engine.connect() as conn:
                    # 在 SQLAlchemy 2.0 中需要使用 text() 包装
                    from sqlalchemy import text
                    conn.execute(text("PRAGMA journal_mode=WAL;"))
                    conn.commit()
                    print("✅ SQLite WAL模式已启用")
            except Exception as e:
                print(f"⚠️  设置WAL模式失败（非致命错误）: {e}")
                
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise

def drop_db():
    """
    删除所有表（仅用于开发和测试）
    
    Warning: 此操作会删除所有数据！
    """
    try:
        Base.metadata.drop_all(bind=engine)
        print("⚠️  数据库表已删除")
    except Exception as e:
        print(f"❌ 删除数据库表失败: {e}")
        raise

def get_engine():
    """获取数据库引擎"""
    return engine

def create_session() -> Session:
    """创建新的数据库会话"""
    return SessionLocal()