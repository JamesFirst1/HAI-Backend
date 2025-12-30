from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.schemas.upload import UploadResponse, FileDeleteResponse
from app.services.upload import upload_service
from app.services.auth import auth_service
from app.models.user import User

router = APIRouter()

@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传图片文件
    
    Request Body:
    - file: 图片文件 (multipart/form-data)
    
    Returns:
    - success: 是否成功
    - url: 图片访问URL
    """
    try:
        file_url, file_path = await upload_service.upload_image(current_user.id, file)
        
        return UploadResponse(
            success=True,
            url=file_url
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )

@router.post("/avatar", response_model=UploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像
    
    Request Body:
    - file: 头像图片文件 (multipart/form-data)
    
    Returns:
    - success: 是否成功
    - url: 头像访问URL
    """
    try:
        file_url, file_path = await upload_service.upload_image(current_user.id, file, is_avatar=True)
        
        # 更新用户头像URL
        auth_service.update_user_avatar(db, current_user.id, file_url)
        
        return UploadResponse(
            success=True,
            url=file_url
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}"
        )

@router.delete("/image")
async def delete_image(
    image_url: str = Query(..., description="要删除的图片URL"),
    current_user: User = Depends(get_current_user)
):
    """
    删除上传的图片
    
    Query Parameters:
    - image_url: 图片URL
    
    Returns:
    - success: 是否成功
    - message: 提示信息
    """
    try:
        success = upload_service.delete_image(current_user.id, image_url)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found or you don't have permission to delete it"
            )
        
        return FileDeleteResponse(
            success=True,
            message="Image deleted successfully"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )

@router.get("/cleanup")
async def cleanup_old_files(
    days_old: int = Query(30, ge=1, le=365, description="清理多少天前的文件"),
    current_user: User = Depends(get_current_user)
):
    """
    清理用户的旧文件（管理员功能）
    
    Query Parameters:
    - days_old: 清理多少天前的文件 (1-365)
    
    Returns:
    - success: 是否成功
    - deleted_count: 删除的文件数量
    """
    try:
        deleted_count = upload_service.cleanup_old_files(current_user.id, days_old)
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Cleaned up {deleted_count} old files"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup files: {str(e)}"
        )