from pydantic import BaseModel
from typing import Optional

class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None

# 导出所有模型
from app.schemas.auth import *
from app.schemas.chat import *
from app.schemas.memory import *
from app.schemas.upload import *

__all__ = [
    # 基础
    "BaseResponse",
    "ErrorResponse",
    
    # 认证
    "RegisterRequest",
    "LoginRequest",
    "AuthResponse",
    "Token",
    "UserProfile",
    
    # 聊天
    "ChatMessageRequest",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "MessageInHistory",
    
    # 记忆
    "MemoryCreate",
    "MemoryUpdate",
    "MemoryResponse",
    "MemorySearchRequest",
    "MemoryDeleteRequest",
    
    # 上传
    "UploadResponse",
    "FileDeleteResponse",
]