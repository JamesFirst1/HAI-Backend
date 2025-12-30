from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    """文件上传响应"""
    success: bool = True
    url: Optional[str] = None
    message: Optional[str] = None

class FileDeleteResponse(BaseModel):
    """文件删除响应"""
    success: bool = True
    message: Optional[str] = None