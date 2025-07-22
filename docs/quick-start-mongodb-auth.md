# MongoDB用户认证系统快速启动指南

## 🎯 概览

TradingAgents-CN现在支持**MongoDB优先存储**的用户认证系统，提供更好的性能和数据持久化。系统会自动创建默认管理员账户 `admin` / `Trade123456`，让您快速开始使用。

## ⚡ 快速启动（3步搞定）

### 第1步：启动MongoDB

**选项A：使用Docker（推荐）**
```bash
# 一键启动包含MongoDB的完整环境
docker-compose up -d

# 或仅启动MongoDB
docker-compose up -d mongodb
```

**选项B：本地MongoDB**
```bash
# 如果已安装MongoDB，直接启动
mongod
```

### 第2步：配置环境变量（可选）

创建或编辑 `.env` 文件，添加以下配置（如果不配置，将使用默认值）：

```env
# MongoDB连接配置（默认值，可自定义）
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=Trade123456
MONGODB_DATABASE=tradingagents

# 默认管理员账户（默认值，建议修改密码）
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=Trade123456
```

### 第3步：启动Web界面

```bash
# 启动Streamlit Web界面
python -m streamlit run web/app.py

# 或使用启动脚本
python start_web.py
```

## 🔐 立即登录

1. 打开浏览器访问 `http://localhost:8501`
2. 点击侧边栏的 **"🔐 用户认证"**
3. 使用默认管理员账户登录：
   - **用户名**: `admin`
   - **密码**: `Trade123456`

**🎉 完成！您现在已经可以使用MongoDB用户认证系统了！**

## 📊 存储架构说明

### 智能存储策略

```mermaid
graph TD
    A[用户操作] --> B{MongoDB可用?}
    B -->|是| C[MongoDB存储]
    B -->|否| D[JSON文件存储]
    C --> E[同时备份到JSON]
    D --> F[仅JSON存储]
    E --> G[操作完成]
    F --> G
```

### 存储位置

| 存储类型 | 用户数据 | 会话数据 | 备注 |
|---------|---------|---------|------|
| **MongoDB** | `tradingagents.auth_users` | `tradingagents.auth_sessions` | 主要存储 |
| **JSON文件** | `web/data/users.json` | `web/data/sessions.json` | 备份/降级 |

### 自动降级机制

- ✅ **MongoDB可用**: 优先使用MongoDB存储，同时备份到JSON文件
- ❌ **MongoDB不可用**: 自动降级到JSON文件存储
- 🔄 **无缝切换**: 用户无感知的存储切换

## 🛠️ 高级配置

### 自定义MongoDB连接

**方式1：环境变量分离配置**
```env
MONGODB_HOST=your_mongodb_host
MONGODB_PORT=27017
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_DATABASE=tradingagents
MONGODB_AUTH_SOURCE=admin
```

**方式2：连接字符串（优先级更高）**
```env
MONGODB_CONNECTION_STRING=mongodb://username:password@host:port/database
```

### 自定义默认管理员

```env
# 自定义管理员账户
DEFAULT_ADMIN_USERNAME=myadmin
DEFAULT_ADMIN_PASSWORD=MySecurePassword123!

# 重启应用后生效
```

### 安全配置建议

```env
# 生产环境安全配置
MONGODB_USERNAME=your_secure_username
MONGODB_PASSWORD=your_very_secure_password_123!@#
DEFAULT_ADMIN_PASSWORD=admin_secure_password_456!@#

# 启用SSL连接（如果MongoDB支持）
MONGODB_CONNECTION_STRING=mongodb://user:pass@host:port/db?ssl=true
```

## 🔍 验证安装

### 运行演示脚本

```bash
# 运行认证系统演示，验证所有功能
python examples/auth_demo.py
```

演示脚本将显示：
- ✅ MongoDB连接状态
- ✅ 默认管理员账户验证
- ✅ 用户注册、登录、会话管理
- ✅ 数据存储测试

### 检查存储状态

```python
# 检查MongoDB连接状态
from web.utils.mongodb_auth_adapter import get_mongodb_auth_adapter

adapter = get_mongodb_auth_adapter()
if adapter:
    print("✅ MongoDB认证系统已启用")
    stats = adapter.get_user_stats()
    print(f"用户数: {stats['total_users']}")
else:
    print("📄 使用JSON文件存储")
```

### Web界面验证

1. 访问 `http://localhost:8501`
2. 查看侧边栏是否显示用户信息区域
3. 点击 **"🔐 用户认证"** 进入登录页面
4. 使用默认管理员账户登录测试

## 🚀 功能特性

### 🔐 认证功能
- [x] 用户注册（邮箱验证、密码强度检查）
- [x] 安全登录（SHA-256密码哈希）
- [x] 自动会话管理（24小时过期）
- [x] 默认管理员账户自动创建

### 👤 用户管理
- [x] 个人资料管理（姓名、邮箱、偏好设置）
- [x] 密码修改功能
- [x] 角色系统（普通用户、管理员）
- [x] 用户统计信息

### 🗄️ 存储优化
- [x] MongoDB优先存储
- [x] JSON文件智能降级
- [x] 数据双重备份
- [x] 自动过期会话清理

### 🛡️ 安全特性
- [x] 密码哈希加密（SHA-256）
- [x] 安全会话令牌
- [x] 自动过期保护
- [x] 唯一索引约束

## 📝 使用示例

### 用户注册
```python
from web.utils.user_manager import get_user_manager

user_manager = get_user_manager()
success, message = user_manager.register_user(
    username="newuser",
    email="user@example.com",
    password="secure123",
    full_name="新用户"
)
```

### 用户登录
```python
# 用户认证
is_valid, message, user_data = user_manager.authenticate_user("newuser", "secure123")

if is_valid:
    # 创建会话
    token = user_manager.create_session("newuser")
    print(f"登录成功，会话令牌: {token}")
```

### 会话验证
```python
# 验证会话
is_valid, username = user_manager.validate_session(token)
if is_valid:
    print(f"用户 {username} 会话有效")
```

## 🔧 故障排除

### MongoDB连接问题

**问题**: `MongoDB连接失败`
```bash
# 检查MongoDB服务状态
docker ps | grep mongo
# 或
systemctl status mongod
```

**解决方案**:
1. 确保MongoDB服务正在运行
2. 检查用户名密码是否正确
3. 验证网络连接

### 默认管理员问题

**问题**: `无法登录默认管理员账户`

**解决方案**:
```python
# 手动重置默认管理员
python examples/auth_demo.py
# 查看演示脚本中的默认管理员检查部分
```

### 数据存储问题

**问题**: `数据没有保存到MongoDB`

**解决方案**:
1. 检查环境变量配置
2. 查看应用日志中的MongoDB连接状态
3. 确认数据库权限设置

## 📈 性能优化

### MongoDB索引优化

系统自动创建以下索引：
- 用户名唯一索引 (`username`)
- 邮箱唯一索引 (`email`)
- 会话令牌唯一索引 (`token`)
- 过期时间索引 (`expires_at`)

### 存储性能对比

| 操作 | MongoDB | JSON文件 | 性能提升 |
|------|---------|----------|----------|
| 用户查询 | ~1ms | ~10ms | **10x** |
| 会话验证 | ~1ms | ~5ms | **5x** |
| 批量操作 | ~5ms | ~50ms | **10x** |
| 并发访问 | 高 | 低 | **显著** |

## 🚀 下一步

### 1. 体验Web界面
- 访问 `http://localhost:8501`
- 使用默认管理员登录
- 注册新用户测试

### 2. 自定义配置
- 修改默认管理员密码
- 配置自己的MongoDB实例
- 调整会话过期时间

### 3. 集成到分析流程
- 在股票分析前检查用户认证
- 保存用户的分析历史
- 实现个性化设置

---

## 🎉 恭喜！

您已经成功启用了MongoDB用户认证系统！

**接下来您可以**：
- 🔐 使用 `admin` / `Trade123456` 登录系统
- 👤 创建和管理用户账户
- 📊 享受高性能的数据存储
- 🛡️ 获得安全的会话保护

**建议**：
1. 💡 修改默认管理员密码以确保安全
2. 🗄️ 使用MongoDB以获得最佳性能
3. 🔄 定期备份用户数据 