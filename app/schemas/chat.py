from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ChatMessageRequest(BaseModel):
    """聊天消息请求模型"""
    text: str = Field(..., min_length=1, max_length=2000)
    imageUrl: Optional[str] = None
    memoryId: Optional[str] = None
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatMessageResponse(BaseModel):
    """聊天消息响应模型（标准格式）"""
    msgId: str
    sender: str
    intent: str
    content: str
    meta: Dict[str, Any] = Field(default_factory=dict)
    timestamp: int

class ChatHistoryResponse(BaseModel):
    """聊天历史响应模型"""
    status: str = "success"
    data: Dict[str, Any]

class MessageInHistory(BaseModel):
    """历史消息项"""
    msgId: str
    sender: str
    content: str
    intent: str
    meta: Dict[str, Any] = {}
    timestamp: int