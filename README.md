# Heart Voice Backend

AI陪伴应用后端，提供记忆保存、对话陪伴等功能。

## 功能特性

- 👤 用户认证（注册/登录/JWT）
- 💬 智能对话（支持多种意图识别）
- 📸 记忆保存（图片+文字描述）
- 🔍 记忆搜索和管理
- 🖼️ 文件上传（图片/头像）
- 📊 完整的API文档

## 技术栈

- **后端框架**: FastAPI
- **数据库**: SQLite/SQLAlchemy
- **认证**: JWT/Bcrypt
- **文件处理**: Pillow/aiofiles
- **API文档**: Swagger UI/ReDoc

## 快速开始

### 1. 环境设置

```bash
# 克隆项目
git clone <repository-url>
cd KB-Backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env
# 编辑.env文件，设置JWT_SECRET_KEY等