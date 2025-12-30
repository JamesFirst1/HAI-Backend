from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.message import Message
from app.utils.helpers import generate_message_id

class MessageCRUD:
    """消息数据库操作类"""
    
    @staticmethod
    def get_by_id(db: Session, message_id: str) -> Optional[Message]:
        """根据ID获取消息"""
        return db.query(Message).filter(Message.id == message_id).first()
    
    @staticmethod
    def get_by_msg_id(db: Session, msg_id: str) -> Optional[Message]:
        """根据msgId获取消息"""
        return db.query(Message).filter(Message.msgId == msg_id).first()
    
    @staticmethod
    def get_user_messages(
        db: Session, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 100,
        days: Optional[int] = None
    ) -> List[Message]:
        """获取用户的消息历史"""
        query = db.query(Message).filter(Message.user_id == user_id)
        
        # 如果指定了天数，只获取最近N天的消息
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(Message.timestamp >= cutoff_date)
        
        return query.order_by(Message.timestamp.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(
        db: Session, 
        user_id: str,
        msg_id: str,
        sender: str,
        intent: str,
        content: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> Message:
        """创建新消息"""
        message = Message(
            user_id=user_id,
            msgId=msg_id,
            sender=sender,
            intent=intent,
            content=content,
            meta=meta or {}
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def create_user_message(
        db: Session,
        user_id: str,
        content: str,
        intent: str = "chat",
        meta: Optional[Dict[str, Any]] = None
    ) -> Message:
        """创建用户消息"""
        msg_id = generate_message_id("user")
        return MessageCRUD.create(db, user_id, msg_id, "user", intent, content, meta)
    
    @staticmethod
    def create_ai_message(
        db: Session,
        user_id: str,
        content: str,
        intent: str = "chat",
        meta: Optional[Dict[str, Any]] = None
    ) -> Message:
        """创建AI消息"""
        msg_id = generate_message_id("ai")
        return MessageCRUD.create(db, user_id, msg_id, "ai", intent, content, meta)
    
    @staticmethod
    def update_meta(
        db: Session, 
        message_id: str, 
        meta_updates: Dict[str, Any]
    ) -> Optional[Message]:
        """更新消息的元数据"""
        message = MessageCRUD.get_by_id(db, message_id)
        if not message:
            return None
        
        # 更新元数据
        if message.meta is None:
            message.meta = {}
        
        message.meta.update(meta_updates)
        db.commit()
        db.refresh(message)
        return message
    
    @staticmethod
    def delete(db: Session, message_id: str) -> bool:
        """删除消息"""
        message = MessageCRUD.get_by_id(db, message_id)
        if not message:
            return False
        
        db.delete(message)
        db.commit()
        return True
    
    @staticmethod
    def delete_user_messages(db: Session, user_id: str, days_older_than: int = 30) -> int:
        """删除用户指定天数前的旧消息"""
        cutoff_date = datetime.now() - timedelta(days=days_older_than)
        
        result = db.query(Message).filter(
            Message.user_id == user_id,
            Message.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        return result
    
    @staticmethod
    def count_user_messages(db: Session, user_id: str) -> int:
        """统计用户的消息数量"""
        return db.query(Message).filter(Message.user_id == user_id).count()
    
    @staticmethod
    def get_conversation_history(
        db: Session, 
        user_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取用户的对话历史"""
        messages = db.query(Message).filter(
            Message.user_id == user_id
        ).order_by(Message.timestamp.desc()).limit(limit).all()
        
        # 转换为字典格式并反转顺序（最新的在最后）
        messages_dict = [msg.to_dict() for msg in reversed(messages)]
        return messages_dict

# 创建全局实例
message_crud = MessageCRUD()