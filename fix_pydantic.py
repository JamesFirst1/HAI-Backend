# fix_pydantic.py
import os

def fix_pydantic_issue():
    """修复Pydantic 2.x中的regex->pattern问题"""
    schemas_file = "app/schemas/auth.py"
    
    if not os.path.exists(schemas_file):
        print(f"❌ 找不到文件: {schemas_file}")
        return False
    
    with open(schemas_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 替换regex为pattern
    content = content.replace('regex="^[a-zA-Z0-9_]+$"', 'pattern="^[a-zA-Z0-9_]+$"')
    content = content.replace("regex='^(male|female|other)$'", "pattern='^(male|female|other)$'")
    
    with open(schemas_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ 已修复Pydantic兼容性问题")
    return True

if __name__ == "__main__":
    fix_pydantic_issue()