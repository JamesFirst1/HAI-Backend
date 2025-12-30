from fastapi import HTTPException, status
from typing import Optional, Dict, Any

class HeartVoiceException(HTTPException):
    """基础异常类"""
    def __init__(self, 
                 status_code: int = status.HTTP_400_BAD_REQUEST,
                 detail: str = "An error occurred",
                 headers: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class AuthenticationError(HeartVoiceException):
    """认证错误"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class UserAlreadyExistsError(HeartVoiceException):
    """用户已存在"""
    def __init__(self, detail: str = "User already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class UserNotFoundError(HeartVoiceException):
    """用户未找到"""
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class InvalidCredentialsError(HeartVoiceException):
    """无效凭证"""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class MemoryNotFoundError(HeartVoiceException):
    """记忆未找到"""
    def __init__(self, detail: str = "Memory not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class FileUploadError(HeartVoiceException):
    """文件上传错误"""
    def __init__(self, detail: str = "File upload failed"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class InvalidFileTypeError(HeartVoiceException):
    """无效文件类型"""
    def __init__(self, detail: str = "Invalid file type"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class FileTooLargeError(HeartVoiceException):
    """文件过大"""
    def __init__(self, detail: str = "File too large"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)