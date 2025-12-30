from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.memory import Memory
from app.core.exceptions import MemoryNotFoundError
from app.utils.helpers import extract_labels_from_text

class MemoryCRUD:
    """记忆数据库操作类"""
    
    @staticmethod
    def get_by_id(db: Session, memory_id: str, include_deleted: bool = False) -> Optional[Memory]:
        """根据ID获取记忆"""
        query = db.query(Memory).filter(Memory.id == memory_id)
        if not include_deleted:
            query = query.filter(Memory.is_deleted == False)
        return query.first()
    
    @staticmethod
    def get_user_memories(
        db: Session, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Memory]:
        """获取用户的所有记忆"""
        query = db.query(Memory).filter(Memory.user_id == user_id)
        if not include_deleted:
            query = query.filter(Memory.is_deleted == False)
        
        return query.order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(
        db: Session, 
        user_id: str,
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        title: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Memory:
        """创建新记忆"""
        # 如果提供了描述但没提供标签，从描述中提取标签
        if description and not labels:
            labels = extract_labels_from_text(description)
        
        memory = Memory(
            user_id=user_id,
            image_url=image_url,
            description=description,
            title=title,
            labels=labels or []
        )
        
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory
    
    @staticmethod
    def update(
        db: Session, 
        memory_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[Memory]:
        """更新记忆信息"""
        memory = MemoryCRUD.get_by_id(db, memory_id)
        if not memory:
            return None
        
        # 更新字段
        for key, value in update_data.items():
            if hasattr(memory, key) and value is not None:
                setattr(memory, key, value)
        
        # 如果更新了描述，重新提取标签
        if 'description' in update_data and update_data['description']:
            memory.labels = extract_labels_from_text(update_data['description'])
        
        db.commit()
        db.refresh(memory)
        return memory
    
    @staticmethod
    def delete(db: Session, memory_id: str, delete_type: str = "memory") -> bool:
        """
        删除记忆
        
        Args:
            delete_type: "photo" - 只删除照片；"memory" - 删除整个记忆
        """
        memory = MemoryCRUD.get_by_id(db, memory_id, include_deleted=True)
        if not memory:
            return False
        
        if delete_type == "photo":
            # 只删除照片，保留记忆信息
            memory.image_url = None
        else:
            # 删除整个记忆（软删除）
            memory.is_deleted = True
        
        db.commit()
        return True
    
    @staticmethod
    def search(
        db: Session, 
        user_id: str, 
        query: str,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Memory]:
        """搜索用户的记忆"""
        # 简单的文本搜索，可以在description和title中搜索
        search_query = f"%{query.lower()}%"
        
        memories = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_deleted == False,
            or_(
                Memory.description.ilike(search_query),
                Memory.title.ilike(search_query),
                Memory.labels.contains([query.lower()])  # 假设labels是JSON字段
            )
        ).order_by(Memory.created_at.desc()).offset(skip).limit(limit).all()
        
        return memories
    
    @staticmethod
    def count_user_memories(db: Session, user_id: str) -> int:
        """统计用户的记忆数量"""
        return db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_deleted == False
        ).count()
    
    @staticmethod
    def get_recent_memories(
        db: Session, 
        user_id: str, 
        limit: int = 10
    ) -> List[Memory]:
        """获取用户最近的记忆"""
        return db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_deleted == False
        ).order_by(Memory.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def user_owns_memory(db: Session, user_id: str, memory_id: str) -> bool:
        """检查记忆是否属于指定用户"""
        memory = MemoryCRUD.get_by_id(db, memory_id)
        return memory and memory.user_id == user_id

# 创建全局实例
memory_crud = MemoryCRUD()