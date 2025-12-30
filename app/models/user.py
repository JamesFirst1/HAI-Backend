from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import Base

def generate_uuid():
    """生成UUID字符串"""
    return str(uuid.uuid4())

class User(Base):
    """
    用户模型
    
    存储用户的基本信息、认证信息和偏好设置
    """
    __tablename__ = "users"
    
    # 主键和唯一标识
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # 认证信息
    password_hash = Column(String(255), nullable=False)
    
    # 个人信息
    name = Column(String(100), nullable=False)
    gender = Column(String(20))
    age = Column(Integer)
    
    # 头像和个性化
    avatar_url = Column(String(500))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 状态标志
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 关系
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        将用户对象转换为字典
        
        Args:
            include_sensitive: 是否包含敏感信息
            
        Returns:
            dict: 用户信息字典
        """
        data = {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_verified": self.is_verified
        }
        
        if include_sensitive:
            data["password_hash"] = self.password_hash
            
        return data
    
    def __repr__(self) -> str:
        return f"<User(id='{self.id}', username='{self.username}', name='{self.name}')>"