"""
核心工具模块
提供安全、LLM、异常处理和中间件等核心功能
"""
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    create_user_token
)

from app.core.llm import (
    MockLLMService,
    llm_service
)

from app.core.exceptions import (
    HeartVoiceException,
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    MemoryNotFoundError,
    FileUploadError,
    InvalidFileTypeError,
    FileTooLargeError
)

from app.core.middleware import (
    LoggingMiddleware,
    CORSMiddleware
)

__all__ = [
    # 安全
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "create_user_token",
    
    # LLM服务
    "MockLLMService",
    "llm_service",
    
    # 异常
    "HeartVoiceException",
    "AuthenticationError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "MemoryNotFoundError",
    "FileUploadError",
    "InvalidFileTypeError",
    "FileTooLargeError",
    
    # 中间件
    "LoggingMiddleware",
    "CORSMiddleware",
]