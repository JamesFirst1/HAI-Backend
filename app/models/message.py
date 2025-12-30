from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from app.database import Base

class Message(Base):
    """
    消息模型
    
    存储用户与AI的对话消息
    """
    __tablename__ = "messages"
    
    # 主键和唯一标识
    id = Column(String(36), primary_key=True, default=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    
    # 外键关联
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 消息标识
    msgId = Column(String(50), index=True)  # 对应API文档中的msgId
    sender = Column(String(20))  # "user" 或 "ai"
    intent = Column(String(50))  # chat, save_memory, search_memory等
    
    # 消息内容
    content = Column(Text)
    meta = Column(JSON)  # 存储额外的元数据
    
    # 关联的记忆ID（如果有）
    memory_id = Column(String(36), ForeignKey("memories.id"), nullable=True, index=True)
    
    # 时间戳
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # 消息顺序（用于排序）
    sequence = Column(Integer, autoincrement=True)
    
    # 关系
    user = relationship("User", back_populates="messages")
    memory = relationship("Memory")
    
    def to_dict(self) -> dict:
        """
        将消息对象转换为字典
        
        Returns:
            dict: 消息信息字典
        """
        return {
            "msgId": self.msgId,
            "sender": self.sender,
            "intent": self.intent,
            "content": self.content,
            "meta": self.meta or {},
            "memory_id": self.memory_id,
            "timestamp": int(self.timestamp.timestamp()) if self.timestamp else None
        }
    
    def to_api_format(self) -> dict:
        """
        转换为API文档中定义的格式
        
        Returns:
            dict: API格式的消息字典
        """
        return {
            "msgId": self.msgId,
            "sender": self.sender,
            "intent": self.intent,
            "content": self.content,
            "meta": self.meta or {},
            "timestamp": int(self.timestamp.timestamp()) if self.timestamp else None
        }
    
    def __repr__(self) -> str:
        return f"<Message(msgId='{self.msgId}', sender='{self.sender}', intent='{self.intent}')>"