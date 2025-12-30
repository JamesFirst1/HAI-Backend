from typing import List, Dict, Any, Optional
from datetime import datetime

from app.crud.memory import memory_crud
from app.crud.message import message_crud
from app.schemas.memory import MemoryCreate, MemoryUpdate
from app.core.exceptions import MemoryNotFoundError

class MemoryService:
    """记忆服务"""
    
    @staticmethod
    def create_memory(
        db,
        user_id: str,
        memory_data: MemoryCreate
    ) -> Dict[str, Any]:
        """
        创建新记忆
        
        Returns:
            dict: 创建的记忆信息
        """
        memory = memory_crud.create(
            db, user_id, 
            memory_data.image_url,
            memory_data.description,
            memory_data.title,
            memory_data.labels
        )
        
        return memory.to_dict()
    
    @staticmethod
    def get_memory(db, memory_id: str) -> Dict[str, Any]:
        """
        获取记忆详情
        
        Returns:
            dict: 记忆信息
        """
        memory = memory_crud.get_by_id(db, memory_id)
        if not memory:
            raise MemoryNotFoundError(f"Memory {memory_id} not found")
        
        return memory.to_dict()
    
    @staticmethod
    def get_user_memories(
        db,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取用户的所有记忆
        
        Returns:
            list: 记忆列表
        """
        memories = memory_crud.get_user_memories(db, user_id, skip, limit)
        return [memory.to_dict() for memory in memories]
    
    @staticmethod
    def update_memory(
        db,
        memory_id: str,
        update_data: MemoryUpdate
    ) -> Dict[str, Any]:
        """
        更新记忆
        
        Returns:
            dict: 更新后的记忆信息
        """
        # 转换为字典
        update_dict = {
            key: value for key, value in update_data.dict().items() 
            if value is not None
        }
        
        memory = memory_crud.update(db, memory_id, update_dict)
        if not memory:
            raise MemoryNotFoundError(f"Memory {memory_id} not found")
        
        return memory.to_dict()
    
    @staticmethod
    def delete_memory(
        db,
        memory_id: str,
        delete_type: str = "memory"
    ) -> Dict[str, Any]:
        """
        删除记忆
        
        Args:
            delete_type: "photo" - 只删除照片；"memory" - 删除整个记忆
        
        Returns:
            dict: 操作结果
        """
        success = memory_crud.delete(db, memory_id, delete_type)
        if not success:
            raise MemoryNotFoundError(f"Memory {memory_id} not found")
        
        return {
            "success": True,
            "message": "Memory deleted successfully" if delete_type == "memory" else "Photo deleted successfully",
            "memoryId": memory_id
        }
    
    @staticmethod
    def search_memories(
        db,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索记忆
        
        Returns:
            list: 搜索结果
        """
        memories = memory_crud.search(db, user_id, query, limit=limit)
        return [memory.to_dict() for memory in memories]
    
    @staticmethod
    def add_description_to_memory(
        db,
        memory_id: str,
        description: str
    ) -> Dict[str, Any]:
        """
        为记忆添加描述
        
        Returns:
            dict: 更新后的记忆信息
        """
        memory = memory_crud.update(db, memory_id, {"description": description})
        if not memory:
            raise MemoryNotFoundError(f"Memory {memory_id} not found")
        
        return memory.to_dict()

# 创建全局实例
memory_service = MemoryService()