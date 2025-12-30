from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import json
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用信息
    APP_NAME: str = "Heart Voice Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/database/heartvoice.db"
    
    # JWT配置
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # 文件上传配置
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://localhost:8000"]
    
    # OpenAI配置（可选）
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            """解析环境变量"""
            if field_name == "CORS_ORIGINS":
                try:
                    # 尝试解析JSON数组
                    return json.loads(raw_val)
                except json.JSONDecodeError:
                    # 如果是逗号分隔的字符串
                    return [origin.strip() for origin in raw_val.split(",") if origin.strip()]
            return raw_val
    
    @field_validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """验证数据库URL"""
        if v.startswith("sqlite"):
            # 确保SQLite数据库文件路径存在
            db_path = v.replace("sqlite:///", "")
            if db_path:
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return v
    
    @field_validator('UPLOAD_DIR')
    def validate_upload_dir(cls, v):
        """验证上传目录"""
        os.makedirs(v, exist_ok=True)
        return v
    
    @field_validator('JWT_SECRET_KEY')
    def validate_jwt_secret_key(cls, v):
        """验证JWT密钥"""
        if v == "your-super-secret-jwt-key-change-this-in-production":
            import warnings
            warnings.warn(
                "⚠️  警告：您正在使用默认的JWT_SECRET_KEY，这在生产环境中是不安全的！",
                UserWarning
            )
        return v

# 创建全局配置实例
settings = Settings()