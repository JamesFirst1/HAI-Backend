from pydantic import BaseModel, Field, validator
from typing import Optional

class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    age: Optional[int] = Field(None, ge=0, le=120)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str

class AuthResponse(BaseModel):
    """认证响应模型"""
    success: bool = True
    userId: Optional[str] = None
    token: Optional[str] = None
    message: Optional[str] = None

class Token(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"

class UserProfile(BaseModel):
    """用户信息模型"""
    id: str
    username: str
    name: str
    gender: Optional[str]
    age: Optional[int]
    avatar_url: Optional[str]
    created_at: Optional[str]