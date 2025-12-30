from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.core.security import get_password_hash
from app.core.exceptions import UserNotFoundError, UserAlreadyExistsError

class UserCRUD:
    """用户数据库操作类"""
    
    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username, User.is_active == True).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户（分页）"""
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, user_data: RegisterRequest) -> User:
        """创建新用户"""
        # 检查用户名是否已存在
        existing_user = UserCRUD.get_by_username(db, user_data.username)
        if existing_user:
            raise UserAlreadyExistsError(f"Username '{user_data.username}' already exists")
        
        # 创建用户
        user = User(
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
            name=user_data.name,
            gender=user_data.gender,
            age=user_data.age
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update(
        db: Session, 
        user_id: str, 
        update_data: Dict[str, Any]
    ) -> Optional[User]:
        """更新用户信息"""
        user = UserCRUD.get_by_id(db, user_id)
        if not user:
            return None
        
        # 更新字段
        for key, value in update_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_name(db: Session, user_id: str, new_name: str) -> Optional[User]:
        """更新用户名称"""
        user = UserCRUD.get_by_id(db, user_id)
        if not user:
            return None
        
        user.name = new_name
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_avatar(db: Session, user_id: str, avatar_url: str) -> Optional[User]:
        """更新用户头像"""
        user = UserCRUD.get_by_id(db, user_id)
        if not user:
            return None
        
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_password(db: Session, user_id: str, new_password: str) -> bool:
        """更新用户密码"""
        user = UserCRUD.get_by_id(db, user_id)
        if not user:
            return False
        
        user.password_hash = get_password_hash(new_password)
        db.commit()
        return True
    
    @staticmethod
    def delete(db: Session, user_id: str) -> bool:
        """软删除用户（标记为不活跃）"""
        user = UserCRUD.get_by_id(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def verify_user(db: Session, username: str, password: str) -> Optional[User]:
        """验证用户凭据"""
        user = UserCRUD.get_by_username(db, username)
        if not user:
            return None
        
        from app.core.security import verify_password
        if verify_password(password, user.password_hash):
            return user
        return None
    
    @staticmethod
    def exists(db: Session, user_id: str) -> bool:
        """检查用户是否存在"""
        return db.query(User).filter(User.id == user_id, User.is_active == True).count() > 0

# 创建全局实例
user_crud = UserCRUD()