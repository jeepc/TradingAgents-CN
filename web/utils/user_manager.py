#!/usr/bin/env python3
"""
用户管理模块
处理用户注册、登录、会话管理等功能
"""

import hashlib
import json
import os
import secrets
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List, Any
import streamlit as st

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web_auth')

# 导入MongoDB认证适配器
try:
    from .mongodb_auth_adapter import get_mongodb_auth_adapter, MongoDBAuthAdapter
    MONGODB_AUTH_AVAILABLE = True
except ImportError:
    MONGODB_AUTH_AVAILABLE = False
    get_mongodb_auth_adapter = None
    MongoDBAuthAdapter = None

class UserManager:
    """用户管理器"""
    
    def __init__(self, users_file: str = "web/data/users.json", sessions_file: str = "web/data/sessions.json"):
        """初始化用户管理器"""
        self.users_file = Path(users_file)
        self.sessions_file = Path(sessions_file)
        
        # 确保数据目录存在
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self.sessions_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 会话过期时间（默认24小时）
        self.session_expire_hours = 24
        
        # 密码复杂度要求
        self.min_password_length = 6
        
        # 先初始化MongoDB适配器
        self.mongodb_adapter = None
        self._init_mongodb_adapter()
        
        # 然后初始化文件（可能会用到mongodb_adapter）
        self._init_files()
        
        # 最后创建默认管理员账户
        self._create_default_admin()
        
        logger.info("✅ 用户管理器初始化完成")
    
    def _init_files(self):
        """初始化用户和会话文件"""
        if not self.users_file.exists():
            self._save_users({})
            logger.info(f"📄 创建用户文件: {self.users_file}")
        
        if not self.sessions_file.exists():
            self._save_sessions({})
            logger.info(f"📄 创建会话文件: {self.sessions_file}")
    
    def _init_mongodb_adapter(self):
        """初始化MongoDB适配器"""
        if not MONGODB_AUTH_AVAILABLE:
            logger.info("📄 MongoDB认证适配器不可用，使用JSON文件存储")
            self.mongodb_adapter = None
            return
        
        try:
            self.mongodb_adapter = get_mongodb_auth_adapter()
            if self.mongodb_adapter:
                logger.info("✅ MongoDB认证适配器初始化成功")
            else:
                logger.warning("⚠️ MongoDB认证适配器连接失败，将使用JSON文件存储")
        except Exception as e:
            logger.error(f"❌ MongoDB认证适配器初始化失败: {e}")
            self.mongodb_adapter = None
    
    def _create_default_admin(self):
        """创建默认管理员账户"""
        default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Trade123456")
        
        # 检查管理员是否已存在
        admin_exists = False
        
        # 优先从MongoDB检查
        if self.mongodb_adapter:
            admin_user = self.mongodb_adapter.load_user(default_username)
            admin_exists = admin_user is not None
        
        # 如果MongoDB中不存在，检查JSON文件
        if not admin_exists:
            users = self._load_users()
            admin_exists = default_username in users
        
        # 如果管理员不存在，创建默认管理员
        if not admin_exists:
            try:
                success, message = self.register_user(
                    username=default_username,
                    email="admin@tradingagents.local",
                    password=default_password,
                    full_name="系统管理员"
                )
                
                if success:
                    # 设置为管理员角色
                    if self.mongodb_adapter:
                        self.mongodb_adapter.update_user(default_username, {"role": "admin"})
                    else:
                        users = self._load_users()
                        if default_username in users:
                            users[default_username]["role"] = "admin"
                            self._save_users(users)
                    
                    logger.info(f"👑 默认管理员账户已创建: {default_username}")
                else:
                    logger.warning(f"⚠️ 默认管理员账户创建失败: {message}")
            except Exception as e:
                logger.error(f"❌ 创建默认管理员账户时出错: {e}")
    
    def _load_users(self) -> Dict:
        """加载用户数据 - 优先从MongoDB，降级到JSON文件"""
        # 优先尝试从MongoDB加载
        if self.mongodb_adapter:
            try:
                users = self.mongodb_adapter.load_all_users()
                if users:
                    return users
            except Exception as e:
                logger.error(f"❌ 从MongoDB加载用户失败: {e}")
        
        # 降级到JSON文件
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ 加载用户文件失败: {e}")
            return {}
    
    def _save_users(self, users: Dict):
        """保存用户数据 - 同时保存到MongoDB和JSON文件"""
        # 优先保存到MongoDB
        if self.mongodb_adapter:
            try:
                for username, user_data in users.items():
                    self.mongodb_adapter.save_user(user_data)
            except Exception as e:
                logger.error(f"❌ 保存用户到MongoDB失败: {e}")
        
        # 同时保存到JSON文件作为备份
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 保存用户文件失败: {e}")
    
    def _load_sessions(self) -> Dict:
        """加载会话数据 - 优先从MongoDB，降级到JSON文件"""
        # 优先尝试从MongoDB加载
        if self.mongodb_adapter:
            try:
                sessions = self.mongodb_adapter.load_all_sessions()
                if sessions:
                    return sessions
            except Exception as e:
                logger.error(f"❌ 从MongoDB加载会话失败: {e}")
        
        # 降级到JSON文件
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ 加载会话文件失败: {e}")
            return {}
    
    def _save_sessions(self, sessions: Dict):
        """保存会话数据 - 同时保存到MongoDB和JSON文件"""
        # 优先保存到MongoDB
        if self.mongodb_adapter:
            try:
                for token, session_data in sessions.items():
                    self.mongodb_adapter.save_session(session_data)
            except Exception as e:
                logger.error(f"❌ 保存会话到MongoDB失败: {e}")
        
        # 同时保存到JSON文件作为备份
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 保存会话文件失败: {e}")
    
    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_token(self) -> str:
        """生成会话令牌"""
        return secrets.token_urlsafe(32)
    
    def validate_password(self, password: str) -> tuple[bool, List[str]]:
        """验证密码强度"""
        errors = []
        
        if len(password) < self.min_password_length:
            errors.append(f"密码长度至少需要{self.min_password_length}位")
        
        if not any(c.isdigit() for c in password):
            errors.append("密码至少包含一个数字")
        
        if not any(c.isalpha() for c in password):
            errors.append("密码至少包含一个字母")
        
        return len(errors) == 0, errors
    
    def validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def register_user(self, username: str, email: str, password: str, full_name: str = "") -> tuple[bool, str]:
        """注册新用户"""
        try:
            # 验证输入
            if not username or not email or not password:
                return False, "用户名、邮箱和密码不能为空"
            
            if len(username) < 3:
                return False, "用户名至少需要3个字符"
            
            if not self.validate_email(email):
                return False, "邮箱格式不正确"
            
            is_valid, password_errors = self.validate_password(password)
            if not is_valid:
                return False, "密码不符合要求：" + "；".join(password_errors)
            
            # 检查用户是否已存在
            users = self._load_users()
            
            if username in users:
                return False, "用户名已存在"
            
            # 检查邮箱是否已被使用
            for user_data in users.values():
                if user_data.get('email') == email:
                    return False, "邮箱已被使用"
            
            # 创建新用户
            user_data = {
                'email': email,
                'password_hash': self._hash_password(password),
                'full_name': full_name,
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True,
                'role': 'user',  # 可扩展为admin等角色
                'preferences': {
                    'theme': 'default',
                    'default_market': 'A股',
                    'auto_refresh': True
                }
            }
            
            users[username] = user_data
            self._save_users(users)
            
            logger.info(f"👤 新用户注册成功: {username} ({email})")
            return True, "注册成功！"
            
        except Exception as e:
            logger.error(f"❌ 用户注册失败: {e}")
            return False, f"注册失败：{str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> tuple[bool, str, Optional[Dict]]:
        """验证用户登录"""
        try:
            if not username or not password:
                return False, "用户名和密码不能为空", None
            
            users = self._load_users()
            
            if username not in users:
                logger.warning(f"⚠️ 登录失败 - 用户不存在: {username}")
                return False, "用户名或密码错误", None
            
            user_data = users[username]
            
            if not user_data.get('is_active', True):
                logger.warning(f"⚠️ 登录失败 - 用户已被禁用: {username}")
                return False, "用户账户已被禁用", None
            
            # 验证密码
            password_hash = self._hash_password(password)
            if password_hash != user_data['password_hash']:
                logger.warning(f"⚠️ 登录失败 - 密码错误: {username}")
                return False, "用户名或密码错误", None
            
            # 更新最后登录时间
            user_data['last_login'] = datetime.now().isoformat()
            users[username] = user_data
            self._save_users(users)
            
            logger.info(f"✅ 用户登录成功: {username}")
            return True, "登录成功", user_data
            
        except Exception as e:
            logger.error(f"❌ 用户认证失败: {e}")
            return False, f"登录失败：{str(e)}", None
    
    def create_session(self, username: str) -> str:
        """创建用户会话"""
        try:
            token = self._generate_session_token()
            
            # 清理该用户的旧会话
            if self.mongodb_adapter:
                self.mongodb_adapter.delete_user_sessions(username)
            
            # 创建新会话数据
            expire_time = datetime.now() + timedelta(hours=self.session_expire_hours)
            session_data = {
                'token': token,
                'username': username,
                'created_at': datetime.now().isoformat(),
                'expires_at': expire_time.isoformat(),
                'last_activity': datetime.now().isoformat()
            }
            
            # 优先保存到MongoDB
            if self.mongodb_adapter:
                success = self.mongodb_adapter.save_session(session_data)
                if success:
                    logger.info(f"🔑 创建用户会话(MongoDB): {username} -> {token[:8]}...")
                    return token
            
            # 降级到JSON文件
            sessions = self._load_sessions()
            
            # 清理该用户的旧会话
            sessions_to_remove = []
            for session_token, session_info in sessions.items():
                if session_info.get('username') == username:
                    sessions_to_remove.append(session_token)
            
            for old_token in sessions_to_remove:
                del sessions[old_token]
            
            # 添加新会话
            sessions[token] = session_data
            self._save_sessions(sessions)
            
            logger.info(f"🔑 创建用户会话(JSON): {username} -> {token[:8]}...")
            return token
            
        except Exception as e:
            logger.error(f"❌ 创建会话失败: {e}")
            return ""
    
    def validate_session(self, token: str) -> tuple[bool, Optional[str]]:
        """验证会话令牌"""
        try:
            if not token:
                return False, None
            
            # 优先从MongoDB验证
            if self.mongodb_adapter:
                session_data = self.mongodb_adapter.load_session(token)
                if session_data:
                    # 检查会话是否过期
                    expire_time = datetime.fromisoformat(session_data['expires_at'])
                    if datetime.now() > expire_time:
                        # 删除过期会话
                        self.mongodb_adapter.delete_session(token)
                        logger.info(f"🔑 删除过期会话(MongoDB): {token[:8]}...")
                        return False, None
                    
                    # 更新最后活动时间
                    updates = {'last_activity': datetime.now().isoformat()}
                    session_data.update(updates)
                    self.mongodb_adapter.save_session(session_data)
                    
                    return True, session_data['username']
            
            # 降级到JSON文件验证
            sessions = self._load_sessions()
            
            if token not in sessions:
                return False, None
            
            session_data = sessions[token]
            
            # 检查会话是否过期
            expire_time = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expire_time:
                # 删除过期会话
                del sessions[token]
                self._save_sessions(sessions)
                logger.info(f"🔑 删除过期会话(JSON): {token[:8]}...")
                return False, None
            
            # 更新最后活动时间
            session_data['last_activity'] = datetime.now().isoformat()
            sessions[token] = session_data
            self._save_sessions(sessions)
            
            return True, session_data['username']
            
        except Exception as e:
            logger.error(f"❌ 会话验证失败: {e}")
            return False, None
    
    def destroy_session(self, token: str):
        """销毁会话"""
        try:
            if not token:
                return
            
            # 优先从MongoDB删除
            if self.mongodb_adapter:
                session_data = self.mongodb_adapter.load_session(token)
                if session_data:
                    username = session_data.get('username', 'unknown')
                    self.mongodb_adapter.delete_session(token)
                    logger.info(f"🔑 销毁用户会话(MongoDB): {username} -> {token[:8]}...")
                    return
            
            # 降级到JSON文件删除
            sessions = self._load_sessions()
            
            if token in sessions:
                username = sessions[token].get('username', 'unknown')
                del sessions[token]
                self._save_sessions(sessions)
                logger.info(f"🔑 销毁用户会话(JSON): {username} -> {token[:8]}...")
            
        except Exception as e:
            logger.error(f"❌ 销毁会话失败: {e}")
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            users = self._load_users()
            if username in users:
                user_data = users[username].copy()
                # 移除敏感信息
                user_data.pop('password_hash', None)
                return user_data
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取用户信息失败: {e}")
            return None
    
    def update_user_info(self, username: str, updates: Dict) -> tuple[bool, str]:
        """更新用户信息"""
        try:
            users = self._load_users()
            
            if username not in users:
                return False, "用户不存在"
            
            user_data = users[username]
            
            # 允许更新的字段
            allowed_fields = ['full_name', 'email', 'preferences']
            
            for field, value in updates.items():
                if field in allowed_fields:
                    if field == 'email':
                        # 验证邮箱格式
                        if not self.validate_email(value):
                            return False, "邮箱格式不正确"
                        
                        # 检查邮箱是否已被其他用户使用
                        for other_username, other_user_data in users.items():
                            if other_username != username and other_user_data.get('email') == value:
                                return False, "邮箱已被使用"
                    
                    user_data[field] = value
            
            user_data['updated_at'] = datetime.now().isoformat()
            users[username] = user_data
            self._save_users(users)
            
            logger.info(f"👤 用户信息更新成功: {username}")
            return True, "信息更新成功"
            
        except Exception as e:
            logger.error(f"❌ 更新用户信息失败: {e}")
            return False, f"更新失败：{str(e)}"
    
    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """修改密码"""
        try:
            users = self._load_users()
            
            if username not in users:
                return False, "用户不存在"
            
            user_data = users[username]
            
            # 验证旧密码
            old_password_hash = self._hash_password(old_password)
            if old_password_hash != user_data['password_hash']:
                return False, "当前密码错误"
            
            # 验证新密码
            is_valid, password_errors = self.validate_password(new_password)
            if not is_valid:
                return False, "新密码不符合要求：" + "；".join(password_errors)
            
            # 更新密码
            user_data['password_hash'] = self._hash_password(new_password)
            user_data['password_changed_at'] = datetime.now().isoformat()
            users[username] = user_data
            self._save_users(users)
            
            logger.info(f"🔐 用户密码修改成功: {username}")
            return True, "密码修改成功"
            
        except Exception as e:
            logger.error(f"❌ 修改密码失败: {e}")
            return False, f"修改失败：{str(e)}"
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        try:
            total_cleaned = 0
            
            # 优先清理MongoDB中的过期会话
            if self.mongodb_adapter:
                mongo_cleaned = self.mongodb_adapter.cleanup_expired_sessions()
                total_cleaned += mongo_cleaned
            
            # 同时清理JSON文件中的过期会话
            sessions = self._load_sessions()
            current_time = datetime.now()
            
            expired_sessions = []
            for token, session_data in sessions.items():
                expire_time = datetime.fromisoformat(session_data['expires_at'])
                if current_time > expire_time:
                    expired_sessions.append(token)
            
            for token in expired_sessions:
                del sessions[token]
            
            if expired_sessions:
                self._save_sessions(sessions)
                total_cleaned += len(expired_sessions)
            
            if total_cleaned > 0:
                logger.info(f"🧹 清理了 {total_cleaned} 个过期会话")
            
        except Exception as e:
            logger.error(f"❌ 清理过期会话失败: {e}")
    
    def get_user_stats(self) -> Dict:
        """获取用户统计信息"""
        try:
            # 优先从MongoDB获取统计
            if self.mongodb_adapter:
                stats = self.mongodb_adapter.get_user_stats()
                if stats and stats['total_users'] > 0:
                    return stats
            
            # 降级到JSON文件统计
            users = self._load_users()
            sessions = self._load_sessions()
            
            active_sessions = 0
            current_time = datetime.now()
            
            for session_data in sessions.values():
                expire_time = datetime.fromisoformat(session_data['expires_at'])
                if current_time <= expire_time:
                    active_sessions += 1
            
            return {
                'total_users': len(users),
                'active_sessions': active_sessions,
                'total_sessions': len(sessions)
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户统计失败: {e}")
            return {'total_users': 0, 'active_sessions': 0, 'total_sessions': 0}


# 全局用户管理器实例
_user_manager = None

def get_user_manager() -> UserManager:
    """获取全局用户管理器实例"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager


def check_authentication() -> tuple[bool, Optional[str]]:
    """检查用户是否已登录"""
    # 从session state获取会话令牌
    token = st.session_state.get('auth_token')
    
    if not token:
        return False, None
    
    user_manager = get_user_manager()
    is_valid, username = user_manager.validate_session(token)
    
    if not is_valid:
        # 清除无效会话
        if 'auth_token' in st.session_state:
            del st.session_state['auth_token']
        if 'username' in st.session_state:
            del st.session_state['username']
    
    return is_valid, username


def require_authentication():
    """装饰器：要求用户登录"""
    is_authenticated, username = check_authentication()
    
    if not is_authenticated:
        st.error("⚠️ 请先登录后访问此功能")
        st.stop()
    
    return username


def logout_user():
    """用户登出"""
    token = st.session_state.get('auth_token')
    
    if token:
        user_manager = get_user_manager()
        user_manager.destroy_session(token)
    
    # 清除session state
    for key in ['auth_token', 'username', 'user_info']:
        if key in st.session_state:
            del st.session_state[key]
    
    logger.info("👋 用户已登出")


def login_user(username: str, password: str) -> tuple[bool, str]:
    """用户登录"""
    user_manager = get_user_manager()
    
    # 认证用户
    is_valid, message, user_data = user_manager.authenticate_user(username, password)
    
    if is_valid:
        # 创建会话
        token = user_manager.create_session(username)
        
        if token:
            # 保存到session state
            st.session_state['auth_token'] = token
            st.session_state['username'] = username
            st.session_state['user_info'] = user_data
            
            logger.info(f"👤 用户登录成功: {username}")
            return True, "登录成功！"
        else:
            return False, "创建会话失败"
    
    return False, message 