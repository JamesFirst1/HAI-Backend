from typing import Dict, Any, Optional, List
from datetime import datetime
import re

from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.crud.message import message_crud
from app.crud.memory import memory_crud
from app.crud.user import user_crud
from app.core.llm import llm_service
from app.core.exceptions import MemoryNotFoundError
from app.utils.helpers import generate_ai_message_id, format_timestamp

class ChatService:
    """聊天服务"""
    
    def __init__(self):
        # 意图识别模式
        self.intent_patterns = {
            "save_memory": [
                r"save.*memory", r"want.*save.*memory", r"keep.*memory",
                r"remember.*this", r"store.*memory"
            ],
            "search_memory": [
                r"search.*memory", r"find.*memory", r"look.*for.*memory",
                r"show.*memory", r"show.*photos", r"find.*photos"
            ],
            "delete_memory": [
                r"delete.*memory", r"remove.*memory", r"don't.*want.*keep",
                r"delete.*photo", r"remove.*photo"
            ],
            "edit_memory": [
                r"edit.*memory", r"change.*memory", r"update.*memory",
                r"modify.*memory", r"change.*description"
            ],
            "update_name": [
                r"change.*name", r"update.*name", r"new.*name", 
                r"call.*me", r"name.*should.*be"
            ],
            "update_avatar": [
                r"change.*picture", r"update.*avatar", r"new.*profile",
                r"change.*profile.*picture", r"update.*profile"
            ],
            "update_password": [
                r"change.*password", r"update.*password", r"new.*password",
                r"reset.*password", r"forgot.*password"
            ]
        }
    
    def detect_intent(self, text: str, current_context: Optional[Dict[str, Any]] = None) -> str:
        """
        检测用户消息的意图
        
        Args:
            text: 用户消息文本
            current_context: 当前对话上下文
        
        Returns:
            str: 意图类型
        """
        text_lower = text.lower()
        
        # 如果有当前上下文，优先使用上下文中的意图
        if current_context and "expected_intent" in current_context:
            return current_context["expected_intent"]
        
        # 检查是否有记忆ID，如果有可能是编辑或删除
        if current_context and "memory_id" in current_context:
            if "change" in text_lower or "edit" in text_lower or "update" in text_lower:
                return "edit_memory"
            elif "delete" in text_lower or "remove" in text_lower:
                return "delete_memory"
        
        # 模式匹配
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        # 默认意图
        return "chat"
    
    def process_message(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest,
        current_context: Optional[Dict[str, Any]] = None
    ) -> ChatMessageResponse:
        """
        处理用户消息并生成AI响应
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            request: 用户消息请求
            current_context: 当前对话上下文
        
        Returns:
            ChatMessageResponse: AI响应
        """
        # 保存用户消息到数据库
        user_msg = message_crud.create_user_message(
            db, user_id, request.text, "user", {"imageUrl": request.imageUrl}
        )
        
        # 检测意图
        intent = self.detect_intent(request.text, current_context)
        
        # 处理不同的意图
        if intent == "save_memory":
            return self._handle_save_memory(db, user_id, request, current_context)
        elif intent == "search_memory":
            return self._handle_search_memory(db, user_id, request)
        elif intent == "delete_memory":
            return self._handle_delete_memory(db, user_id, request, current_context)
        elif intent == "edit_memory":
            return self._handle_edit_memory(db, user_id, request, current_context)
        elif intent == "update_name":
            return self._handle_update_name(db, user_id, request, current_context)
        elif intent == "update_avatar":
            return self._handle_update_avatar(db, user_id, request, current_context)
        elif intent == "update_password":
            return self._handle_update_password(db, user_id, request, current_context)
        else:
            return self._handle_normal_chat(db, user_id, request)
    
    def _handle_normal_chat(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest
    ) -> ChatMessageResponse:
        """处理普通聊天"""
        # 获取用户信息用于个性化回复
        user = user_crud.get_by_id(db, user_id)
        user_data = {"current_name": user.name} if user else {}
        
        # 生成AI响应
        ai_response = llm_service.generate_response("chat", user_data)
        
        # 保存AI消息到数据库
        message_crud.create(
            db, user_id, ai_response["msgId"], "ai", 
            ai_response["intent"], ai_response["content"], ai_response["meta"]
        )
        
        return ChatMessageResponse(**ai_response)
    
    def _handle_save_memory(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest,
        current_context: Optional[Dict[str, Any]]
    ) -> ChatMessageResponse:
        """处理保存记忆"""
        # 检查是否已上传图片
        if request.imageUrl:
            # 创建记忆记录
            memory = memory_crud.create(
                db, user_id, request.imageUrl, None, None, None
            )
            
            # 生成添加描述的响应
            ai_response = llm_service.generate_response(
                "add_description", 
                context={"memory_id": memory.id, "image_url": request.imageUrl}
            )
            ai_response["meta"]["memoryId"] = memory.id
            ai_response["meta"]["imageUrl"] = request.imageUrl
        else:
            # 请求上传图片
            ai_response = llm_service.generate_response("save_memory")
        
        # 保存AI消息到数据库
        message_crud.create(
            db, user_id, ai_response["msgId"], "ai", 
            ai_response["intent"], ai_response["content"], ai_response["meta"]
        )
        
        return ChatMessageResponse(**ai_response)
    
    def _handle_search_memory(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest
    ) -> ChatMessageResponse:
        """处理搜索记忆"""
        # 简单的关键词提取（从消息中提取搜索词）
        search_keywords = request.text.lower()
        
        # 搜索记忆
        memories = memory_crud.search(db, user_id, search_keywords, limit=5)
        
        # 生成响应
        ai_response = llm_service.generate_response("search_memory")
        
        # 添加搜索结果到元数据
        if memories:
            memory_data = memories[0].to_dict()
            ai_response["meta"].update(memory_data)
        
        # 保存AI消息到数据库
        message_crud.create(
            db, user_id, ai_response["msgId"], "ai", 
            ai_response["intent"], ai_response["content"], ai_response["meta"]
        )
        
        return ChatMessageResponse(**ai_response)
    
    def _handle_delete_memory(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest,
        current_context: Optional[Dict[str, Any]]
    ) -> ChatMessageResponse:
        """处理删除记忆"""
        memory_id = request.memoryId
        
        if not memory_id:
            # 如果没有提供memoryId，需要先确定要删除哪个记忆
            # 这里可以添加逻辑来根据上下文确定记忆
            ai_response = llm_service.generate_response("confirm_delete")
        else:
            # 确认删除
            ai_response = llm_service.generate_response("confirm_delete")
            ai_response["meta"]["memoryId"] = memory_id
        
        # 保存AI消息到数据库
        message_crud.create(
            db, user_id, ai_response["msgId"], "ai", 
            ai_response["intent"], ai_response["content"], ai_response["meta"]
        )
        
        return ChatMessageResponse(**ai_response)
    
    def _handle_edit_memory(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest,
        current_context: Optional[Dict[str, Any]]
    ) -> ChatMessageResponse:
        """处理编辑记忆"""
        memory_id = request.memoryId
        
        if not memory_id:
            # 需要先确定要编辑哪个记忆
            ai_response = llm_service.generate_response("edit_memory")
        else:
            # 获取记忆信息
            memory = memory_crud.get_by_id(db, memory_id)
            if not memory:
                raise MemoryNotFoundError("Memory not found")
            
            # 询问要编辑什么
            ai_response = llm_service.generate_response("edit_memory")
            ai_response["meta"]["memoryId"] = memory_id
        
        # 保存AI消息到数据库
        message_crud.create(
            db, user_id, ai_response["msgId"], "ai", 
            ai_response["intent"], ai_response["content"], ai_response["meta"]
        )
        
        return ChatMessageResponse(**ai_response)
    
    def _handle_update_name(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest,
        current_context: Optional[Dict[str, Any]]
    ) -> ChatMessageResponse:
        """处理更新名称"""
        user = user_crud.get_by_id(db, user_id)
        
        # 生成响应
        ai_response = llm_service.generate_response(
            "update_name", 
            user_data={"current_name": user.name if user else "User"}
        )
        
        # 保存AI消息到数据库
        message_crud.create(
            db, user_id, ai_response["msgId"], "ai", 
            ai_response["intent"], ai_response["content"], ai_response["meta"]
        )
        
        return ChatMessageResponse(**ai_response)
    
    def _handle_update_avatar(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest,
        current_context: Optional[Dict[str, Any]]
    ) -> ChatMessageResponse:
        """处理更新头像"""
        # 生成响应
        ai_response = llm_service.generate_response("update_avatar")
        
        # 保存AI消息到数据库
        message_crud.create(
            db, user_id, ai_response["msgId"], "ai", 
            ai_response["intent"], ai_response["content"], ai_response["meta"]
        )
        
        return ChatMessageResponse(**ai_response)
    
    def _handle_update_password(
        self,
        db,
        user_id: str,
        request: ChatMessageRequest,
        current_context: Optional[Dict[str, Any]]
    ) -> ChatMessageResponse:
        """处理更新密码"""
        # 生成响应
        ai_response = llm_service.generate_response("update_password")
        
        # 保存AI消息到数据库
        message_crud.create(
            db, user_id, ai_response["msgId"], "ai", 
            ai_response["intent"], ai_response["content"], ai_response["meta"]
        )
        
        return ChatMessageResponse(**ai_response)
    
    def get_conversation_history(
        self,
        db,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        Returns:
            list: 对话历史列表
        """
        return message_crud.get_conversation_history(db, user_id, limit)

# 创建全局实例
chat_service = ChatService()