from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemorySearchRequest,
    MemoryDeleteRequest
)
from app.services.memory import memory_service
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新记忆
    
    Request Body:
    - image_url: 图片URL (可选)
    - description: 描述 (可选)
    - title: 标题 (可选)
    - labels: 标签列表 (可选)
    
    Returns:
    - id: 记忆ID
    - image_url: 图片URL
    - description: 描述
    - title: 标题
    - labels: 标签列表
    - date: 记忆日期
    - created_at: 创建时间
    """
    try:
        return memory_service.create_memory(db, current_user.id, memory_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create memory: {str(e)}"
        )

@router.get("/", response_model=List[MemoryResponse])
async def get_user_memories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有记忆
    
    Query Parameters:
    - skip: 跳过数量 (分页)
    - limit: 返回数量 (分页，最大1000)
    
    Returns:
    - List[MemoryResponse]: 记忆列表
    """
    try:
        return memory_service.get_user_memories(db, current_user.id, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memories: {str(e)}"
        )

@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取特定记忆详情
    
    Path Parameters:
    - memory_id: 记忆ID
    
    Returns:
    - MemoryResponse: 记忆详情
    """
    try:
        # 先检查记忆是否属于当前用户
        from app.crud.memory import memory_crud
        if not memory_crud.user_owns_memory(db, current_user.id, memory_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this memory"
            )
        
        return memory_service.get_memory(db, memory_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory: {str(e)}"
        )

@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    update_data: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新记忆
    
    Path Parameters:
    - memory_id: 记忆ID
    
    Request Body:
    - description: 描述 (可选)
    - title: 标题 (可选)
    - labels: 标签列表 (可选)
    
    Returns:
    - MemoryResponse: 更新后的记忆
    """
    try:
        # 先检查记忆是否属于当前用户
        from app.crud.memory import memory_crud
        if not memory_crud.user_owns_memory(db, current_user.id, memory_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this memory"
            )
        
        return memory_service.update_memory(db, memory_id, update_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update memory: {str(e)}"
        )

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    delete_type: str = Query("memory", regex="^(photo|memory)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除记忆
    
    Path Parameters:
    - memory_id: 记忆ID
    
    Query Parameters:
    - delete_type: 删除类型 (photo: 只删除照片, memory: 删除整个记忆)
    
    Returns:
    - success: 是否成功
    - message: 提示信息
    - memoryId: 记忆ID
    """
    try:
        # 先检查记忆是否属于当前用户
        from app.crud.memory import memory_crud
        if not memory_crud.user_owns_memory(db, current_user.id, memory_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this memory"
            )
        
        return memory_service.delete_memory(db, memory_id, delete_type)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory: {str(e)}"
        )

@router.post("/search")
async def search_memories(
    search_request: MemorySearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    搜索记忆
    
    Request Body:
    - query: 搜索关键词
    - limit: 返回数量 (默认10)
    
    Returns:
    - success: 是否成功
    - results: 搜索结果列表
    - count: 结果数量
    """
    try:
        results = memory_service.search_memories(
            db, current_user.id, search_request.query, search_request.limit
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search memories: {str(e)}"
        )

@router.post("/{memory_id}/description")
async def add_description_to_memory(
    memory_id: str,
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为记忆添加描述
    
    Path Parameters:
    - memory_id: 记忆ID
    
    Request Body:
    - description: 描述文本
    
    Returns:
    - MemoryResponse: 更新后的记忆
    """
    try:
        description = request_data.get("description")
        if not description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="description is required"
            )
        
        # 先检查记忆是否属于当前用户
        from app.crud.memory import memory_crud
        if not memory_crud.user_owns_memory(db, current_user.id, memory_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this memory"
            )
        
        return memory_service.add_description_to_memory(db, memory_id, description)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add description: {str(e)}"
        )