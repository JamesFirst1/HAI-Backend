from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, 
    LoginRequest, 
    AuthResponse,
    Token,
    UserProfile
)
from app.services.auth import auth_service
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    Request Body:
    - username: 用户名 (3-50字符，字母数字下划线)
    - password: 密码 (6-100字符)
    - name: 昵称 (1-100字符)
    - gender: 性别 (可选，male/female/other)
    - age: 年龄 (可选，0-120)
    
    Returns:
    - success: 是否成功
    - userId: 用户ID
    - token: JWT令牌
    """
    try:
        return auth_service.register(db, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    Request Body:
    - username: 用户名
    - password: 密码
    
    Returns:
    - success: 是否成功
    - userId: 用户ID
    - token: JWT令牌
    """
    try:
        return auth_service.login(db, login_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2兼容的令牌端点（可选）
    """
    from app.schemas.auth import LoginRequest
    from app.core.exceptions import InvalidCredentialsError
    
    try:
        login_data = LoginRequest(username=form_data.username, password=form_data.password)
        response = auth_service.login(db, login_data)
        return Token(access_token=response.token, token_type="bearer")
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserProfile)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息
    
    Returns:
    - id: 用户ID
    - username: 用户名
    - name: 昵称
    - gender: 性别
    - age: 年龄
    - avatar_url: 头像URL
    - created_at: 创建时间
    """
    try:
        return auth_service.get_current_user_profile(db, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.post("/update-name")
async def update_user_name(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户昵称
    
    Request Body:
    - newName: 新昵称
    
    Returns:
    - newName: 更新后的昵称
    """
    try:
        new_name = request_data.get("newName")
        if not new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="newName is required"
            )
        
        return auth_service.update_user_name(db, current_user.id, new_name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update name: {str(e)}"
        )

@router.post("/update-password")
async def update_user_password(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户密码
    
    Request Body:
    - newPassword: 新密码
    
    Returns:
    - success: 是否成功
    - message: 提示信息
    """
    try:
        new_password = request_data.get("newPassword")
        if not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="newPassword is required"
            )
        
        return auth_service.update_user_password(db, current_user.id, new_password)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update password: {str(e)}"
        )