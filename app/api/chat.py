from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database import get_db
from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    MessageInHistory
)
from app.services.chat import chat_service
from app.models.user import User

router = APIRouter()

# 内存中的对话上下文（生产环境应使用Redis等存储）
conversation_contexts: Dict[str, Dict[str, Any]] = {}

@router.post("/send", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送聊天消息
    
    根据用户的文本消息和当前上下文，生成AI响应。
    支持普通聊天、保存记忆、搜索记忆、删除记忆、修改记忆等功能。
    
    Request Body:
    - text: 用户消息文本
    - imageUrl: 可选，图片URL
    - memoryId: 可选，记忆ID
    - extra: 可选，额外数据
    
    Returns:
    - msgId: 消息ID
    - sender: 发送者 (ai)
    - intent: 意图类型
    - content: AI回复内容
    - meta: 元数据
    - timestamp: 时间戳
    """
    try:
        # 获取当前用户的对话上下文
        user_context = conversation_contexts.get(current_user.id, {})
        
        # 处理消息
        response = chat_service.process_message(
            db, current_user.id, request, user_context
        )
        
        # 更新上下文
        if response.intent in ["save_memory", "add_description", "edit_memory", "confirm_delete", "update_password"]:
            # 这些意图需要后续交互，保存到上下文
            user_context["expected_intent"] = response.intent
            if request.memoryId:
                user_context["memory_id"] = request.memoryId
            conversation_contexts[current_user.id] = user_context
        elif response.intent in ["memory_saved", "memory_deleted", "memory_updated", "name_changed", "avatar_updated", "password_updated"]:
            # 这些意图完成了一个流程，清除上下文
            if current_user.id in conversation_contexts:
                del conversation_contexts[current_user.id]
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取聊天历史
    
    Query Parameters:
    - limit: 返回的消息数量，默认50
    
    Returns:
    - status: 状态 (success)
    - data: 包含messages列表
    """
    try:
        # 获取对话历史
        messages = chat_service.get_conversation_history(db, current_user.id, limit)
        
        return ChatHistoryResponse(
            status="success",
            data={"messages": messages}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )

@router.get("/context")
async def get_conversation_context(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前对话上下文（调试用）
    
    Returns:
    - context: 当前用户的对话上下文
    """
    user_context = conversation_contexts.get(current_user.id, {})
    return {"context": user_context}

@router.post("/clear-context")
async def clear_conversation_context(
    current_user: User = Depends(get_current_user)
):
    """
    清除当前对话上下文
    
    Returns:
    - success: 是否成功
    """
    if current_user.id in conversation_contexts:
        del conversation_contexts[current_user.id]
    return {"success": True}