#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表结构和初始数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import logging
from app.database import init_db, drop_db, create_session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.memory import Memory
from app.models.message import Message
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_data(db, create_demo: bool = True, create_test: bool = False):
    """
    创建示例数据
    
    Args:
        db: 数据库会话
        create_demo: 是否创建演示用户
        create_test: 是否创建测试用户
    """
    try:
        # 创建演示用户（如果不存在）
        if create_demo:
            existing_demo = db.query(User).filter(User.username == "demo_user").first()
            if not existing_demo:
                demo_user = User(
                    username="demo_user",
                    password_hash=get_password_hash("demo123"),
                    name="Demo User",
                    gender="other",
                    age=35,
                    avatar_url="/uploads/demo/avatar.png"
                )
                db.add(demo_user)
                db.flush()  # 获取用户ID但不提交
                
                logger.info(f"创建演示用户: {demo_user.username} (ID: {demo_user.id})")
                
                # 创建演示记忆
                demo_memory1 = Memory(
                    user_id=demo_user.id,
                    image_url="/uploads/demo/sunset.jpg",
                    description="A beautiful sunset at the beach with my family. The sky was painted in orange and purple hues.",
                    title="Family Beach Sunset",
                    labels=["family", "beach", "sunset", "vacation", "happy"],
                    memory_date=datetime.now() - timedelta(days=30)
                )
                db.add(demo_memory1)
                
                demo_memory2 = Memory(
                    user_id=demo_user.id,
                    image_url="/uploads/demo/birthday.jpg",
                    description="My daughter's 5th birthday party. She was so excited about her unicorn cake!",
                    title="Daughter's Birthday",
                    labels=["daughter", "birthday", "party", "cake", "family"],
                    memory_date=datetime.now() - timedelta(days=60),
                    is_favorite=True
                )
                db.add(demo_memory2)
                
                # 创建演示消息
                demo_messages = [
                    Message(
                        user_id=demo_user.id,
                        msgId="msg-demo-001",
                        sender="user",
                        intent="chat",
                        content="Hello, I'd like to save a memory",
                        meta={}
                    ),
                    Message(
                        user_id=demo_user.id,
                        msgId="ai-demo-001",
                        sender="ai",
                        intent="save_memory",
                        content="Of course. Please upload a photo you'd like to save as a memory.",
                        meta={"needImage": True}
                    ),
                    Message(
                        user_id=demo_user.id,
                        msgId="msg-demo-002",
                        sender="user",
                        intent="chat",
                        content="I want to see my beach memories",
                        meta={}
                    ),
                    Message(
                        user_id=demo_user.id,
                        msgId="ai-demo-002",
                        sender="ai",
                        intent="search_memory",
                        content="Here are the memories I found:",
                        meta={
                            "memoryId": "mem-001",
                            "imageUrl": "/uploads/demo/sunset.jpg",
                            "description": "A beautiful sunset at the beach with my family.",
                            "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                        }
                    )
                ]
                
                for msg in demo_messages:
                    db.add(msg)
                
                logger.info("创建演示数据成功")
        
        # 创建测试用户（如果不存在）
        if create_test:
            existing_test = db.query(User).filter(User.username == "test_user").first()
            if not existing_test:
                test_user = User(
                    username="test_user",
                    password_hash=get_password_hash("test123"),
                    name="Test User",
                    gender="female",
                    age=28
                )
                db.add(test_user)
                logger.info(f"创建测试用户: {test_user.username}")
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        logger.error(f"创建示例数据失败: {e}")
        raise

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Heart Voice 数据库管理工具")
    parser.add_argument("--init", action="store_true", help="初始化数据库（创建表）")
    parser.add_argument("--drop", action="store_true", help="删除所有表（危险操作！）")
    parser.add_argument("--seed", action="store_true", help="创建示例数据")
    parser.add_argument("--demo-only", action="store_true", help="只创建演示用户")
    parser.add_argument("--test-only", action="store_true", help="只创建测试用户")
    parser.add_argument("--all", action="store_true", help="初始化数据库并创建所有示例数据")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Heart Voice 数据库管理工具")
    print("=" * 60)
    
    try:
        if args.drop:
            # 删除数据库
            confirm = input("⚠️  警告：这将删除所有数据！是否继续？(y/N): ")
            if confirm.lower() == 'y':
                drop_db()
                print("✅ 数据库表已删除")
            else:
                print("操作已取消")
                return
        
        if args.init or args.all:
            # 初始化数据库
            print("\n正在初始化数据库...")
            init_db()
            print("✅ 数据库初始化成功")
        
        if args.seed or args.all or args.demo_only or args.test_only:
            # 创建示例数据
            print("\n正在创建示例数据...")
            
            # 创建数据库会话
            db = create_session()
            
            try:
                create_demo = args.demo_only or args.seed or args.all
                create_test = args.test_only or args.seed or args.all
                
                create_sample_data(db, create_demo, create_test)
                print("✅ 示例数据创建成功")
            finally:
                db.close()
        
        if not any(vars(args).values()):
            # 默认操作：初始化数据库并创建演示数据
            print("\n正在初始化数据库...")
            init_db()
            print("✅ 数据库初始化成功")
            
            print("\n正在创建示例数据...")
            db = create_session()
            try:
                create_sample_data(db, create_demo=True, create_test=False)
                print("✅ 示例数据创建成功")
            finally:
                db.close()
        
        print("\n" + "=" * 60)
        print("数据库管理完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()