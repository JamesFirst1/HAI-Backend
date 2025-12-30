# fix_db.py - 在项目根目录运行
import os

def fix_database_file():
    """修复数据库文件中的 SQLAlchemy 2.0 问题"""
    database_file = "app/database.py"
    
    if not os.path.exists(database_file):
        print(f"❌ 找不到文件: {database_file}")
        print("请确保在项目根目录运行此脚本")
        return False
    
    with open(database_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 要替换的代码
    old_code = '''        # 如果是SQLite，设置WAL模式以获得更好的并发性能
        if "sqlite" in settings.DATABASE_URL:
            with engine.connect() as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                print("✅ SQLite WAL模式已启用")'''
    
    new_code = '''        # 如果是SQLite，设置WAL模式以获得更好的并发性能
        if "sqlite" in settings.DATABASE_URL:
            try:
                with engine.connect() as conn:
                    # 在 SQLAlchemy 2.0 中需要使用 text() 包装
                    from sqlalchemy import text
                    conn.execute(text("PRAGMA journal_mode=WAL;"))
                    conn.commit()
                    print("✅ SQLite WAL模式已启用")
            except Exception as e:
                print(f"⚠️  设置WAL模式失败（非致命错误）: {e}")'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(database_file, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ 已修复 database.py 中的 SQLAlchemy 2.0 问题")
        return True
    elif new_code in content:
        print("✅ database.py 已经是最新版本")
        return True
    else:
        print("❌ 无法定位需要修复的代码")
        print("请手动检查 app/database.py 文件")
        return False

if __name__ == "__main__":
    print("正在修复数据库连接问题...")
    print(f"当前目录: {os.getcwd()}")
    print(f"数据库文件位置: app/database.py")
    
    if fix_database_file():
        print("\n✅ 修复完成！现在请运行：")
        print("python scripts/init_database.py")
        print("或直接启动: python run.py --reload")