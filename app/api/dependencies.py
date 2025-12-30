from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.crud.user import user_crud

# Bearer认证方案
security = HTTPBearer(auto_error=False)  # 设置为auto_error=False以支持可选认证

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户依赖项
    
    Raises:
        HTTPException: 如果认证失败
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_crud.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    可选获取当前用户依赖项
    用于不需要强制登录的接口
    """
    if credentials is None:
        return None
    
    try:
        payload = decode_access_token(credentials.credentials)
        if payload is None:
            return None
            
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = user_crud.get_by_id(db, user_id)
        return user
    except (JWTError, AttributeError):
        return None