from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.database import Base

class Memory(Base):
    """
    记忆模型
    
    存储用户的记忆，包括图片、描述、标签等信息
    """
    __tablename__ = "memories"
    
    # 主键和唯一标识
    id = Column(String(36), primary_key=True, default=lambda: f"mem-{uuid.uuid4().hex[:8]}")
    
    # 外键关联
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 记忆内容
    image_url = Column(String(500))
    description = Column(Text)
    title = Column(String(200))
    labels = Column(JSON)  # 存储标签列表，如 ["family", "vacation", "beach"]
    
    # 时间信息
    memory_date = Column(DateTime(timezone=True), server_default=func.now())  # 记忆的实际日期
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 状态标志
    is_deleted = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    
    # 关系
    user = relationship("User", back_populates="memories")
    
    def to_dict(self) -> dict:
        """
        将记忆对象转换为字典
        
        Returns:
            dict: 记忆信息字典
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_url": self.image_url,
            "description": self.description,
            "title": self.title,
            "labels": self.labels or [],
            "memory_date": self.memory_date.isoformat() if self.memory_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_deleted": self.is_deleted,
            "is_favorite": self.is_favorite
        }
    
    def get_thumbnail_url(self) -> str:
        """
        获取缩略图URL（如果有图片）
        
        Returns:
            str: 缩略图URL或原图URL
        """
        if not self.image_url:
            return None
        
        # 这里可以添加缩略图处理逻辑
        # 例如：在原图URL基础上添加缩略图后缀
        return self.image_url.replace(".jpg", "_thumb.jpg") if self.image_url.endswith(".jpg") else self.image_url
    
    def __repr__(self) -> str:
        return f"<Memory(id='{self.id}', user_id='{self.user_id}', title='{self.title[:20]}...')>"