from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MemoryCreate(BaseModel):
    """创建记忆模型"""
    image_url: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None
    labels: Optional[List[str]] = None

class MemoryUpdate(BaseModel):
    """更新记忆模型"""
    description: Optional[str] = None
    title: Optional[str] = None
    labels: Optional[List[str]] = None

class MemoryResponse(BaseModel):
    """记忆响应模型"""
    id: str
    image_url: Optional[str]
    description: Optional[str]
    title: Optional[str]
    labels: List[str] = []
    date: Optional[str]
    created_at: Optional[str]

class MemorySearchRequest(BaseModel):
    """搜索记忆请求"""
    query: str
    limit: int = 10

class MemoryDeleteRequest(BaseModel):
    """删除记忆请求"""
    memoryId: str
    delete_type: str = "photo"  # "photo" 或 "memory"