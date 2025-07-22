# 用户认证系统使用指南

## 🎯 概览

TradingAgents-CN 现在支持完整的用户认证系统，包括用户注册、登录、会话管理、用户资料管理等功能。该系统**优先使用MongoDB存储**，在MongoDB不可用时自动降级到JSON文件存储，为您的股票分析数据提供安全保护，并支持个性化设置。

## ✨ 功能特性

### 🔐 核心认证功能
- **用户注册**: 支持邮箱验证和密码强度检查
- **安全登录**: SHA-256密码哈希加密
- **会话管理**: 自动过期的安全会话令牌
- **自动登出**: 24小时会话过期保护

### 👤 用户管理功能
- **个人资料**: 修改姓名、邮箱等基本信息
- **密码管理**: 安全的密码修改功能
- **偏好设置**: 个性化界面和默认设置
- **角色系统**: 支持普通用户和管理员角色

### 🗄️ 存储架构
- **MongoDB优先**: 用户数据和会话优先存储在MongoDB数据库
- **智能降级**: MongoDB不可用时自动降级到JSON文件存储
- **默认管理员**: 系统自动创建默认管理员账户 (`admin` / `Trade123456`)
- **数据同步**: 支持MongoDB和JSON文件双重备份

### 🛡️ 安全特性
- **密码加密**: 使用SHA-256哈希算法
- **会话保护**: 令牌自动过期机制
- **数据隔离**: 用户数据安全存储
- **访问控制**: 基于角色的权限管理

## 🚀 快速开始

### 第1步：配置MongoDB（推荐）

**选项A：使用Docker（推荐）**
```bash
# 使用docker-compose启动MongoDB
docker-compose up -d mongodb

# MongoDB将运行在端口27017，用户名admin，密码Trade123456
```

**选项B：本地MongoDB**
```bash
# 安装MongoDB后，创建用户
mongosh
> use admin
> db.createUser({
    user: "admin",
    pwd: "Trade123456",
    roles: ["userAdminAnyDatabase", "readWriteAnyDatabase"]
})
```

### 第2步：配置环境变量

在项目根目录的 `.env` 文件中添加：

```env
# MongoDB配置（如果未配置，将使用默认值）
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=Trade123456
MONGODB_DATABASE=tradingagents

# 默认管理员账户（可自定义）
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=Trade123456
```

### 第3步：启动Web界面

```bash
# 方式1：使用Streamlit直接启动
python -m streamlit run web/app.py

# 方式2：使用启动脚本
python start_web.py
```

### 第4步：访问系统

1. 打开浏览器访问 `http://localhost:8501`
2. 使用默认管理员账户登录：
   - **用户名**: `admin`
   - **密码**: `Trade123456`
3. 或注册新的用户账户

## 📋 存储配置详解

### MongoDB优先模式（推荐）

系统采用**MongoDB优先，JSON降级**的存储策略：

```
📊 存储流程：
1. 🗄️ 尝试连接MongoDB数据库
2. ✅ 成功：使用MongoDB存储用户数据和会话
3. ❌ 失败：自动降级到JSON文件存储
4. 💾 同时维护JSON文件作为备份
```

**MongoDB集合结构**：
- `auth_users`: 用户账户信息
- `auth_sessions`: 登录会话数据

**索引优化**：
- 用户名和邮箱唯一索引
- 会话令牌和过期时间索引
- 查询性能优化

### 默认管理员账户

系统启动时会自动检查并创建默认管理员：

```python
# 默认配置（可通过环境变量修改）
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Trade123456"
```

**创建条件**：
- 系统中不存在同名用户时自动创建
- 自动设置为管理员角色
- 优先检查MongoDB，再检查JSON文件

### 环境变量配置

**MongoDB连接配置**：
```env
# 基本配置
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=Trade123456
MONGODB_DATABASE=tradingagents
MONGODB_AUTH_SOURCE=admin

# 或使用连接字符串（优先级更高）
MONGODB_CONNECTION_STRING=mongodb://admin:Trade123456@localhost:27017/admin
```

**认证系统配置**：
```env
# 默认管理员账户
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=Trade123456

# 分析功能访问控制
REQUIRE_LOGIN_FOR_ANALYSIS=false
```

## 📊 数据存储位置

### MongoDB存储
- **数据库**: `tradingagents`
- **用户集合**: `auth_users`
- **会话集合**: `auth_sessions`
- **连接**: MongoDB://localhost:27017

### JSON文件存储（备份/降级）
- **用户数据**: `web/data/users.json`
- **会话数据**: `web/data/sessions.json`

### 数据格式示例

**MongoDB用户文档**：
```json
{
  "username": "demo_user",
  "email": "demo@example.com",
  "password_hash": "hashed_password",
  "full_name": "演示用户",
  "created_at": "2025-01-01T00:00:00",
  "last_login": "2025-01-01T12:00:00",
  "is_active": true,
  "role": "user",
  "preferences": {
    "theme": "default",
    "default_market": "A股",
    "auto_refresh": true
  },
  "_created_at": "2025-01-01T00:00:00",
  "_updated_at": "2025-01-01T12:00:00"
}
```

**MongoDB会话文档**：
```json
{
  "token": "session_token_here",
  "username": "demo_user",
  "created_at": "2025-01-01T12:00:00",
  "expires_at": "2025-01-02T12:00:00",
  "last_activity": "2025-01-01T15:30:00",
  "_created_at": "2025-01-01T12:00:00"
}
```

## 🔧 配置选项

### MongoDB连接测试

```python
# 测试MongoDB连接
from web.utils.mongodb_auth_adapter import get_mongodb_auth_adapter

adapter = get_mongodb_auth_adapter()
if adapter:
    print("✅ MongoDB连接成功")
else:
    print("❌ MongoDB连接失败，将使用JSON文件存储")
```

### 存储状态检查

```python
# 检查用户管理器状态
from web.utils.user_manager import get_user_manager

user_manager = get_user_manager()
if user_manager.mongodb_adapter:
    print("🗄️ 使用MongoDB存储")
else:
    print("📄 使用JSON文件存储")
```

## 📈 性能优化

### MongoDB性能优化
- **索引优化**: 用户名、邮箱、会话令牌的唯一索引
- **查询优化**: 基于用户名和会话令牌的快速查询
- **过期清理**: 自动清理过期会话，减少存储空间

### 降级机制优化
- **智能检测**: 启动时自动检测MongoDB可用性
- **无缝切换**: MongoDB不可用时自动使用JSON文件
- **双重备份**: 同时维护JSON文件作为数据备份

## 🔍 故障排除

### MongoDB连接问题

1. **连接失败**
   ```
   错误: MongoDB连接失败
   解决: 检查MongoDB服务是否启动，用户名密码是否正确
   ```

2. **认证失败**
   ```
   错误: Authentication failed
   解决: 检查MONGODB_USERNAME和MONGODB_PASSWORD配置
   ```

3. **数据库不存在**
   ```
   错误: Database not found
   解决: MongoDB会自动创建数据库，检查MONGODB_DATABASE配置
   ```

### 系统降级处理

```bash
# 查看系统日志确认存储状态
tail -f logs/web_auth.log

# 查看MongoDB认证适配器日志
grep "MongoDB认证适配器" logs/web_auth.log
```

### 数据迁移

```python
# 从JSON文件迁移到MongoDB
from web.utils.user_manager import get_user_manager

user_manager = get_user_manager()
if user_manager.mongodb_adapter:
    print("数据将自动同步到MongoDB")
else:
    print("请检查MongoDB配置")
```

## 🎮 演示和测试

### 运行演示脚本

```bash
# 运行认证功能演示（会自动创建测试用户）
python examples/auth_demo.py
```

### 测试用户

演示脚本会创建以下测试用户：
- **普通用户**: `demo_user` / `demo123`
- **管理员**: `admin_user` / `admin123`

### 默认管理员

系统自动创建的默认管理员：
- **用户名**: `admin`
- **密码**: `Trade123456`
- **角色**: 管理员

## 🛠️ 开发者信息

### MongoDB集合设计

**用户集合索引**：
```javascript
// 用户名唯一索引
db.auth_users.createIndex({"username": 1}, {"unique": true})

// 邮箱唯一索引
db.auth_users.createIndex({"email": 1}, {"unique": true})

// 创建时间索引
db.auth_users.createIndex({"created_at": 1})
```

**会话集合索引**：
```javascript
// 令牌唯一索引
db.auth_sessions.createIndex({"token": 1}, {"unique": true})

// 用户名索引
db.auth_sessions.createIndex({"username": 1})

// 过期时间索引
db.auth_sessions.createIndex({"expires_at": 1})
```

### API使用示例

```python
from web.utils.user_manager import get_user_manager, check_authentication

# 获取用户管理器
user_manager = get_user_manager()

# 检查存储状态
if user_manager.mongodb_adapter:
    print("✅ MongoDB存储可用")
else:
    print("📄 JSON文件存储模式")

# 检查用户认证状态
is_authenticated, username = check_authentication()
```

---

## 📞 获取帮助

### 技术支持
- **GitHub Issues**: 报告问题和功能请求
- **文档中心**: 查看详细的使用文档
- **演示脚本**: 运行 `python examples/auth_demo.py`

### MongoDB相关
- **MongoDB文档**: https://docs.mongodb.com/
- **PyMongo文档**: https://pymongo.readthedocs.io/
- **连接字符串格式**: https://docs.mongodb.com/manual/reference/connection-string/

---

🎉 **恭喜！您已经了解了完整的用户认证系统使用方法！**

💡 **建议**: 
1. 配置MongoDB以获得最佳性能和数据持久化
2. 使用默认管理员账户 `admin` / `Trade123456` 首次登录
3. 修改默认密码以确保系统安全 