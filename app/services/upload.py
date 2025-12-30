import os
import shutil
from typing import BinaryIO, Tuple
from fastapi import UploadFile

from app.config import settings
from app.utils.file_utils import (
    generate_unique_filename,
    get_file_extension,
    is_valid_image_extension,
    is_valid_image_content,
    validate_file_size,
    save_upload_file,
    create_user_upload_directory,
    delete_file
)
from app.core.exceptions import (
    FileUploadError, 
    InvalidFileTypeError, 
    FileTooLargeError
)

class UploadService:
    """文件上传服务"""
    
    @staticmethod
    async def upload_image(
        user_id: str,
        upload_file: UploadFile,
        is_avatar: bool = False
    ) -> Tuple[str, str]:
        """
        上传图片文件
        
        Args:
            user_id: 用户ID
            upload_file: 上传的文件
            is_avatar: 是否是头像文件
        
        Returns:
            tuple: (文件URL, 文件路径)
        """
        # 验证文件类型
        file_extension = get_file_extension(upload_file.filename)
        if not is_valid_image_extension(file_extension):
            raise InvalidFileTypeError(
                f"Invalid file type. Allowed types: jpg, jpeg, png, gif, bmp, webp"
            )
        
        # 读取文件内容
        file_content = await upload_file.read()
        
        # 验证文件大小
        max_size = 2 * 1024 * 1024 if is_avatar else settings.MAX_UPLOAD_SIZE
        if not validate_file_size(len(file_content), max_size):
            raise FileTooLargeError(
                f"File too large. Maximum size is {max_size // (1024*1024)}MB"
            )
        
        # 验证图片内容
        is_valid, error_info = is_valid_image_content(file_content)
        if not is_valid:
            raise InvalidFileTypeError(f"Invalid image file: {error_info}")
        
        # 重置文件指针
        await upload_file.seek(0)
        
        # 生成唯一文件名
        unique_filename = generate_unique_filename(upload_file.filename)
        
        # 创建用户上传目录
        user_upload_dir = create_user_upload_directory(user_id)
        
        # 保存文件
        file_path = os.path.join(user_upload_dir, unique_filename)
        
        try:
            await save_upload_file(upload_file.file, file_path)
        except Exception as e:
            raise FileUploadError(f"Failed to save file: {str(e)}")
        
        # 生成URL
        file_url = f"/uploads/{user_id}/{unique_filename}"
        
        return file_url, file_path
    
    @staticmethod
    def delete_image(user_id: str, image_url: str) -> bool:
        """
        删除图片文件
        
        Args:
            user_id: 用户ID
            image_url: 图片URL
        
        Returns:
            bool: 是否删除成功
        """
        # 从URL中提取文件名
        # URL格式: /uploads/{user_id}/{filename}
        parts = image_url.split('/')
        if len(parts) < 4 or parts[1] != "uploads" or parts[2] != user_id:
            return False
        
        filename = parts[3]
        file_path = os.path.join(settings.UPLOAD_DIR, user_id, filename)
        
        return delete_file(file_path)
    
    @staticmethod
    def get_user_upload_dir(user_id: str) -> str:
        """
        获取用户的上传目录
        
        Returns:
            str: 目录路径
        """
        return create_user_upload_directory(user_id)
    
    @staticmethod
    def cleanup_old_files(user_id: str, days_old: int = 30) -> int:
        """
        清理用户的旧文件
        
        Args:
            user_id: 用户ID
            days_old: 多少天前的文件视为旧文件
        
        Returns:
            int: 删除的文件数量
        """
        import time
        from datetime import datetime, timedelta
        
        user_dir = os.path.join(settings.UPLOAD_DIR, user_id)
        if not os.path.exists(user_dir):
            return 0
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        for filename in os.listdir(user_dir):
            file_path = os.path.join(user_dir, filename)
            if os.path.isfile(file_path):
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception:
                        pass
        
        return deleted_count

# 创建全局实例
upload_service = UploadService()