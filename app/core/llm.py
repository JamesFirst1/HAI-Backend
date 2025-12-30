from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from app.utils.helpers import generate_ai_message_id

class MockLLMService:
    """
    模拟LLM服务，根据不同的intent返回预设的响应
    在实际部署中可以替换为真实的OpenAI API调用
    """
    
    def __init__(self):
        self.intent_responses = {
            "chat": [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! I'm here to assist you.",
            ],
            "save_memory": "Of course. Please upload a photo you'd like to save as a memory.",
            "add_description": "Your photo is ready. Whenever you're comfortable, you can tell me a few simple words about this memory.",
            "memory_saved": "That's a beautiful memory. I've saved it for you, and you can revisit or edit it anytime.",
            "search_memory": "Here are the memories I found:",
            "confirm_delete": "Of course. Are you sure you want to delete this? You can delete just the photo or the entire memory.",
            "memory_deleted": "Alright, I've deleted this photo for you. You can always add it again later if you wish.",
            "edit_memory": "Absolutely-you can change anything you want. What would you like to update: the title, the description?",
            "ask_new_value": "What would you like it to say instead?",
            "memory_updated": "That's beautiful. I've updated your memory exactly as you described it. You can edit it again anytime-you're always in control.",
            "update_name": "Of course. Your current name is {current_name}. What would you like it to be?",
            "name_changed": "Got it-I've updated your name to {new_name}. You can change it again anytime if you wish.",
            "update_avatar": "Great. When you're ready, please choose a photo from your gallery. I'll only change your avatar after you confirm.",
            "avatar_updated": "All done. Your profile photo has been updated-you can always change it again whenever you like.",
            "update_password": "No problem. To keep your account safe, I'll guide you step by step. Please enter your new password.",
            "confirm_password": "Great. Just one more step-please type it again to confirm.",
            "password_updated": "Perfect. Your password has been updated safely. If you ever forget it, I'll help you recover it. You're doing everything correctly—no need to worry.",
        }
    
    def generate_response(self, 
                         intent: str, 
                         user_data: Optional[Dict[str, Any]] = None,
                         context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据意图生成AI响应
        
        Args:
            intent: 意图类型
            user_data: 用户相关数据（如当前用户名）
            context: 上下文信息（如记忆ID、旧值等）
        """
        # 生成消息ID和时间戳
        msg_id = generate_ai_message_id()
        timestamp = int(datetime.now().timestamp())
        
        # 基础响应结构
        response = {
            "msgId": msg_id,
            "sender": "ai",
            "intent": intent,
            "content": "",
            "meta": {},
            "timestamp": timestamp
        }
        
        # 根据意图生成内容
        if intent in self.intent_responses:
            content_template = self.intent_responses[intent]
            
            # 处理模板中的变量
            if isinstance(content_template, str):
                content = content_template
                if user_data and "current_name" in user_data:
                    content = content.replace("{current_name}", user_data["current_name"])
                if context and "new_name" in context:
                    content = content.replace("{new_name}", context["new_name"])
                response["content"] = content
        
        # 添加特定意图的元数据
        if intent == "save_memory":
            response["meta"]["needImage"] = True
        
        elif intent == "confirm_delete":
            response["meta"]["options"] = ["photo", "memory"]
        
        elif intent == "edit_memory":
            response["meta"]["fields"] = ["title", "description"]
        
        return response

# 创建全局实例
llm_service = MockLLMService()