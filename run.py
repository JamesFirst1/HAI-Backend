#!/usr/bin/env python3
"""
应用启动脚本
提供多种启动方式和配置选项
"""

import os
import sys
import uvicorn
import argparse
from pathlib import Path

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Heart Voice Backend Server")
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level (default: info)"
    )
    
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database before starting server"
    )
    
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Path to environment file (default: .env)"
    )
    
    return parser.parse_args()

def initialize_database():
    """初始化数据库"""
    print("Initializing database...")
    try:
        # 导入数据库初始化函数
        from app.database import init_db
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        sys.exit(1)

def load_environment(env_file):
    """加载环境变量"""
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        print(f"Environment file {env_file} not found, using system environment")

def check_dependencies():
    """检查依赖"""
    print("Checking dependencies...")
    try:
        import fastapi
        import sqlalchemy
        import jose
        import pydantic
        
        print("✓ All dependencies are available")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)

def print_server_info(host, port, reload, workers, log_level):
    """打印服务器信息"""
    print("\n" + "=" * 50)
    print("Heart Voice Backend Server")
    print("=" * 50)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Workers: {workers}")
    print(f"Log Level: {log_level}")
    print("=" * 50)
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/health")
    print("=" * 50 + "\n")

def main():
    """主函数"""
    args = parse_arguments()
    
    # 加载环境变量
    load_environment(args.env_file)
    
    # 检查依赖
    check_dependencies()
    
    # 初始化数据库（如果需要）
    if args.init_db:
        initialize_database()
    
    # 打印服务器信息
    print_server_info(args.host, args.port, args.reload, args.workers, args.log_level)
    
    # 启动服务器
    try:
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,  # reload模式下只使用1个worker
            log_level=args.log_level,
            access_log=True,
            use_colors=True
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()