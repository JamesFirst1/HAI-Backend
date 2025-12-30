from datetime import timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import verify_password, create_user_token
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.crud.user import user_crud
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.utils.helpers import validate_username

class AuthService:
    """认证服务"""
    
    @staticmethod
    def register(db: Session, user_data: RegisterRequest) -> AuthResponse:
        """
        用户注册
        
        Returns:
            AuthResponse: 包含用户ID和令牌的响应
        """
        # 验证用户名格式
        if not validate_username(user_data.username):
            raise ValueError("Invalid username format")
        
        # 创建用户
        try:
            user = user_crud.create(db, user_data)
        except UserAlreadyExistsError as e:
            raise e
        
        # 生成令牌
        token = create_user_token(user.id)
        
        return AuthResponse(
            success=True,
            userId=user.id,
            token=token
        )
    
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> AuthResponse:
        """
        用户登录
        
        Returns:
            AuthResponse: 包含用户ID和令牌的响应
        """
        # 验证用户凭据
        user = user_crud.verify_user(db, login_data.username, login_data.password)
        
        if not user:
            raise InvalidCredentialsError("Invalid username or password")
        
        # 生成令牌
        token = create_user_token(user.id)
        
        return AuthResponse(
            success=True,
            userId=user.id,
            token=token
        )
    
    @staticmethod
    def get_current_user_profile(db: Session, user_id: str) -> Dict[str, Any]:
        """
        获取当前用户信息
        
        Returns:
            dict: 用户信息
        """
        user = user_crud.get_by_id(db, user_id)
        if not user:
            raise InvalidCredentialsError("User not found")
        
        return user.to_dict()
    
    @staticmethod
    def update_user_name(db: Session, user_id: str, new_name: str) -> Dict[str, Any]:
        """
        更新用户名称
        
        Returns:
            dict: 更新后的用户信息
        """
        user = user_crud.update_name(db, user_id, new_name)
        if not user:
            raise InvalidCredentialsError("User not found")
        
        return {"newName": new_name}
    
    @staticmethod
    def update_user_password(db: Session, user_id: str, new_password: str) -> Dict[str, Any]:
        """
        更新用户密码
        
        Returns:
            dict: 操作结果
        """
        success = user_crud.update_password(db, user_id, new_password)
        if not success:
            raise InvalidCredentialsError("User not found")
        
        return {"success": True, "message": "Password updated successfully"}
    
    @staticmethod
    def update_user_avatar(db: Session, user_id: str, avatar_url: str) -> Dict[str, Any]:
        """
        更新用户头像
        
        Returns:
            dict: 更新后的用户信息
        """
        user = user_crud.update_avatar(db, user_id, avatar_url)
        if not user:
            raise InvalidCredentialsError("User not found")
        
        return {"avatarUrl": avatar_url}

# 创建全局实例
auth_service = AuthService()