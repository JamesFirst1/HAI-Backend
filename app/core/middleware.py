import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始
        start_time = time.time()
        
        # 记录请求信息（排除敏感信息）
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        logger.info(f"Request started: {method} {url} from {client_host}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"Request completed: {method} {url} "
                f"Status: {response.status_code} "
                f"Duration: {process_time:.3f}s"
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {method} {url} "
                f"Error: {str(e)} "
                f"Duration: {process_time:.3f}s"
            )
            raise

class CORSMiddleware:
    """自定义CORS中间件"""
    
    @staticmethod
    def add_cors_headers(response: Response, origins: list) -> Response:
        """添加CORS头到响应"""
        response.headers["Access-Control-Allow-Origin"] = ", ".join(origins) if origins else "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-Requested-With, "
            "X-Process-Time, X-API-Key"
        )
        return response