from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import time
import logging
from typing import Dict, Any

from app.config import settings
from app.database import init_db
from app.api import auth, chat, memory, upload
from app.core.middleware import LoggingMiddleware

# 创建日志目录
import os
os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("Starting Heart Voice API...")
    
    # 初始化数据库
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # 创建必要目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data/database", exist_ok=True)
    
    logger.info(f"Application started successfully")
    logger.info(f"API documentation available at /docs")
    
    yield
    
    # 关闭时执行
    logger.info("Shutting down Heart Voice API...")

# 创建FastAPI应用实例
app = FastAPI(
    title="Heart Voice API",
    description="AI陪伴应用后端API - 提供记忆保存、对话陪伴等功能",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置中间件

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"]
)

# GZip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 自定义日志中间件
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    # 记录请求信息
    client_host = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)
    
    logger.info(f"Request started: {method} {url} from {client_host}")
    
    try:
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
        process_time = time.time() - start_time
        logger.error(
            f"Request failed: {method} {url} "
            f"Error: {str(e)} "
            f"Duration: {process_time:.3f}s"
        )
        raise

# 挂载静态文件目录
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: Exception):
    """
    404异常处理器
    """
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Resource not found",
            "detail": f"The requested URL {request.url} was not found"
        }
    )

# 根端点
@app.get("/")
async def root():
    """
    根端点，返回应用信息
    """
    return {
        "message": "Heart Voice API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "author": "Heart Voice Team"
    }

@app.get("/health")
async def health_check():
    """
    健康检查端点
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "heart-voice-api",
        "version": settings.APP_VERSION
    }

# 注册API路由
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])

# API信息端点
@app.get("/api/info")
async def api_info():
    """
    获取API信息
    """
    return {
        "name": "Heart Voice API",
        "version": settings.APP_VERSION,
        "endpoints": [
            {"path": "/api/auth", "description": "用户认证相关接口"},
            {"path": "/api/chat", "description": "聊天对话接口"},
            {"path": "/api/memory", "description": "记忆管理接口"},
            {"path": "/api/upload", "description": "文件上传接口"},
            {"path": "/docs", "description": "API文档(Swagger UI)"},
            {"path": "/redoc", "description": "API文档(ReDoc)"}
        ],
        "authentication": "Bearer Token (JWT)"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )