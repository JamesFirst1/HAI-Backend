import os
import shutil
import uuid
import hashlib
from typing import Tuple, Optional, BinaryIO
from pathlib import Path
from PIL import Image
import io

from app.config import settings
from app.core.exceptions import InvalidFileTypeError, FileTooLargeError

def generate_unique_filename(original_filename: str) -> str:
    """生成唯一的文件名"""
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{ext}"

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower()

def is_valid_image_extension(extension: str) -> bool:
    """检查是否为有效的图片扩展名"""
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    return extension in valid_extensions

def is_valid_image_content(file_content: bytes) -> Tuple[bool, Optional[str]]:
    """通过文件内容验证是否为有效的图片"""
    try:
        image = Image.open(io.BytesIO(file_content))
        image.verify()  # 验证图片完整性
        return True, image.format.lower()
    except Exception as e:
        return False, str(e)

def validate_file_size(file_size: int, max_size: Optional[int] = None) -> bool:
    """验证文件大小"""
    if max_size is None:
        max_size = settings.MAX_UPLOAD_SIZE
    return file_size <= max_size

async def save_upload_file(upload_file: BinaryIO, destination: str) -> str:
    """保存上传的文件到指定路径"""
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file, buffer)
        return destination
    except Exception as e:
        # 如果保存失败，删除可能已创建的部分文件
        if os.path.exists(destination):
            os.remove(destination)
        raise e

def get_file_hash(file_path: str) -> str:
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_user_upload_directory(user_id: str) -> str:
    """创建用户的上传目录"""
    user_dir = os.path.join(settings.UPLOAD_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def get_file_mime_type(file_path: str) -> str:
    """获取文件的MIME类型"""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"

def resize_image(image_path: str, max_size: Tuple[int, int] = (800, 800)) -> str:
    """调整图片大小"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path)
        return image_path
    except Exception as e:
        raise InvalidFileTypeError(f"Failed to resize image: {str(e)}")