#!/usr/bin/env python3
"""
MongoDB用户认证适配器
处理用户数据和会话数据的MongoDB存储
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import asdict

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web_auth_mongodb')

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, DuplicateKeyError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoClient = None


class MongoDBAuthAdapter:
    """MongoDB用户认证适配器"""
    
    def __init__(self, connection_string: str = None, database_name: str = "tradingagents"):
        """初始化MongoDB认证适配器"""
        if not MONGODB_AVAILABLE:
            raise ImportError("pymongo is not installed. Please install it with: pip install pymongo")
        
        # 获取MongoDB连接配置
        self.connection_string = connection_string or self._get_mongodb_connection_string()
        self.database_name = database_name
        
        # 集合名称
        self.users_collection_name = "auth_users"
        self.sessions_collection_name = "auth_sessions"
        
        # 连接对象
        self.client = None
        self.db = None
        self.users_collection = None
        self.sessions_collection = None
        self._connected = False
        
        # 尝试连接
        self._connect()
    
    def _get_mongodb_connection_string(self) -> str:
        """获取MongoDB连接字符串"""
        # 首先尝试从环境变量获取完整连接字符串
        connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        if connection_string:
            return connection_string
        
        # 否则构建连接字符串
        host = os.getenv("MONGODB_HOST", "localhost")
        port = os.getenv("MONGODB_PORT", "27017")
        username = os.getenv("MONGODB_USERNAME", "admin")
        password = os.getenv("MONGODB_PASSWORD", "Trade123456")
        auth_source = os.getenv("MONGODB_AUTH_SOURCE", "admin")
        
        # 构建带认证的连接字符串
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}/{auth_source}"
        else:
            return f"mongodb://{host}:{port}/"
    
    def _connect(self):
        """连接到MongoDB"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000  # 5秒超时
            )
            
            # 测试连接
            self.client.admin.command('ping')
            
            # 选择数据库
            self.db = self.client[self.database_name]
            self.users_collection = self.db[self.users_collection_name]
            self.sessions_collection = self.db[self.sessions_collection_name]
            
            # 创建索引
            self._create_indexes()
            
            self._connected = True
            logger.info(f"✅ MongoDB认证适配器连接成功: {self.database_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB连接失败: {e}")
            self._connected = False
        except Exception as e:
            logger.error(f"❌ MongoDB认证适配器初始化失败: {e}")
            self._connected = False
    
    def _create_indexes(self):
        """创建数据库索引"""
        try:
            # 用户集合索引
            self.users_collection.create_index("username", unique=True)  # 用户名唯一索引
            self.users_collection.create_index("email", unique=True)     # 邮箱唯一索引
            self.users_collection.create_index("created_at")             # 创建时间索引
            self.users_collection.create_index("last_login")             # 最后登录时间索引
            self.users_collection.create_index("is_active")              # 活跃状态索引
            
            # 会话集合索引
            self.sessions_collection.create_index("token", unique=True)   # 令牌唯一索引
            self.sessions_collection.create_index("username")             # 用户名索引
            self.sessions_collection.create_index("expires_at")           # 过期时间索引
            self.sessions_collection.create_index("created_at")           # 创建时间索引
            
            logger.info(f"✅ MongoDB认证索引创建完成")
            
        except Exception as e:
            logger.error(f"⚠️ MongoDB认证索引创建失败: {e}")
    
    def is_connected(self) -> bool:
        """检查是否连接到MongoDB"""
        return self._connected
    
    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """保存用户数据"""
        if not self._connected:
            return False
        
        try:
            # 添加MongoDB特有字段
            user_doc = user_data.copy()
            user_doc['_created_at'] = datetime.now()
            user_doc['_updated_at'] = datetime.now()
            
            # 插入或更新用户
            result = self.users_collection.replace_one(
                {"username": user_data["username"]},
                user_doc,
                upsert=True
            )
            
            if result.upserted_id or result.modified_count > 0:
                logger.info(f"👤 用户数据已保存到MongoDB: {user_data['username']}")
                return True
            else:
                logger.error(f"❌ MongoDB用户保存失败: 未返回有效结果")
                return False
                
        except DuplicateKeyError as e:
            logger.error(f"❌ 用户保存失败: 用户名或邮箱已存在 - {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 保存用户到MongoDB失败: {e}")
            return False
    
    def load_user(self, username: str) -> Optional[Dict[str, Any]]:
        """加载用户数据"""
        if not self._connected:
            return None
        
        try:
            user_doc = self.users_collection.find_one({"username": username})
            
            if user_doc:
                # 移除MongoDB特有字段
                user_doc.pop('_id', None)
                user_doc.pop('_created_at', None)
                user_doc.pop('_updated_at', None)
                
                return user_doc
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 从MongoDB加载用户失败: {e}")
            return None
    
    def load_all_users(self) -> Dict[str, Dict[str, Any]]:
        """加载所有用户数据"""
        if not self._connected:
            return {}
        
        try:
            cursor = self.users_collection.find({})
            users = {}
            
            for user_doc in cursor:
                # 移除MongoDB特有字段
                user_doc.pop('_id', None)
                user_doc.pop('_created_at', None)
                user_doc.pop('_updated_at', None)
                
                username = user_doc.get('username')
                if username:
                    users[username] = user_doc
            
            return users
            
        except Exception as e:
            logger.error(f"❌ 从MongoDB加载所有用户失败: {e}")
            return {}
    
    def update_user(self, username: str, updates: Dict[str, Any]) -> bool:
        """更新用户数据"""
        if not self._connected:
            return False
        
        try:
            # 添加更新时间
            updates_with_timestamp = updates.copy()
            updates_with_timestamp['_updated_at'] = datetime.now()
            
            result = self.users_collection.update_one(
                {"username": username},
                {"$set": updates_with_timestamp}
            )
            
            if result.modified_count > 0:
                logger.info(f"👤 用户数据已更新: {username}")
                return True
            else:
                logger.warning(f"⚠️ 用户更新无变化: {username}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 更新用户MongoDB数据失败: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """删除用户数据"""
        if not self._connected:
            return False
        
        try:
            # 删除用户
            user_result = self.users_collection.delete_one({"username": username})
            
            # 删除用户的所有会话
            session_result = self.sessions_collection.delete_many({"username": username})
            
            if user_result.deleted_count > 0:
                logger.info(f"🗑️ 用户已删除: {username} (同时删除了{session_result.deleted_count}个会话)")
                return True
            else:
                logger.warning(f"⚠️ 用户删除失败，用户不存在: {username}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 删除用户MongoDB数据失败: {e}")
            return False
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """保存会话数据"""
        if not self._connected:
            return False
        
        try:
            # 添加MongoDB特有字段
            session_doc = session_data.copy()
            session_doc['_created_at'] = datetime.now()
            
            # 插入会话
            result = self.sessions_collection.insert_one(session_doc)
            
            if result.inserted_id:
                logger.info(f"🔑 会话已保存到MongoDB: {session_data.get('token', 'unknown')[:8]}...")
                return True
            else:
                logger.error(f"❌ MongoDB会话保存失败: 未返回插入ID")
                return False
                
        except Exception as e:
            logger.error(f"❌ 保存会话到MongoDB失败: {e}")
            return False
    
    def load_session(self, token: str) -> Optional[Dict[str, Any]]:
        """加载会话数据"""
        if not self._connected:
            return None
        
        try:
            session_doc = self.sessions_collection.find_one({"token": token})
            
            if session_doc:
                # 移除MongoDB特有字段
                session_doc.pop('_id', None)
                session_doc.pop('_created_at', None)
                
                return session_doc
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 从MongoDB加载会话失败: {e}")
            return None
    
    def load_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """加载所有会话数据"""
        if not self._connected:
            return {}
        
        try:
            cursor = self.sessions_collection.find({})
            sessions = {}
            
            for session_doc in cursor:
                # 移除MongoDB特有字段
                session_doc.pop('_id', None)
                session_doc.pop('_created_at', None)
                
                token = session_doc.get('token')
                if token:
                    sessions[token] = session_doc
            
            return sessions
            
        except Exception as e:
            logger.error(f"❌ 从MongoDB加载所有会话失败: {e}")
            return {}
    
    def delete_session(self, token: str) -> bool:
        """删除会话数据"""
        if not self._connected:
            return False
        
        try:
            result = self.sessions_collection.delete_one({"token": token})
            
            if result.deleted_count > 0:
                logger.info(f"🔑 会话已删除: {token[:8]}...")
                return True
            else:
                logger.warning(f"⚠️ 会话删除失败，会话不存在: {token[:8]}...")
                return False
                
        except Exception as e:
            logger.error(f"❌ 删除会话MongoDB数据失败: {e}")
            return False
    
    def delete_user_sessions(self, username: str) -> int:
        """删除用户的所有会话"""
        if not self._connected:
            return 0
        
        try:
            result = self.sessions_collection.delete_many({"username": username})
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"🔑 删除了用户 {username} 的 {deleted_count} 个会话")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 删除用户会话失败: {e}")
            return 0
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        if not self._connected:
            return 0
        
        try:
            current_time = datetime.now()
            
            result = self.sessions_collection.delete_many({
                "expires_at": {"$lt": current_time.isoformat()}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"🧹 清理了 {deleted_count} 个过期会话")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 清理过期会话失败: {e}")
            return 0
    
    def get_user_stats(self) -> Dict[str, int]:
        """获取用户统计信息"""
        if not self._connected:
            return {'total_users': 0, 'active_sessions': 0, 'total_sessions': 0}
        
        try:
            total_users = self.users_collection.count_documents({})
            total_sessions = self.sessions_collection.count_documents({})
            
            current_time = datetime.now()
            active_sessions = self.sessions_collection.count_documents({
                "expires_at": {"$gte": current_time.isoformat()}
            })
            
            return {
                'total_users': total_users,
                'active_sessions': active_sessions,
                'total_sessions': total_sessions
            }
            
        except Exception as e:
            logger.error(f"❌ 获取用户统计失败: {e}")
            return {'total_users': 0, 'active_sessions': 0, 'total_sessions': 0}
    
    def close(self):
        """关闭MongoDB连接"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info(f"MongoDB认证适配器连接已关闭")


def get_mongodb_auth_adapter() -> Optional[MongoDBAuthAdapter]:
    """获取MongoDB认证适配器实例"""
    try:
        adapter = MongoDBAuthAdapter()
        if adapter.is_connected():
            return adapter
        else:
            logger.warning("⚠️ MongoDB认证适配器连接失败")
            return None
    except Exception as e:
        logger.error(f"❌ 创建MongoDB认证适配器失败: {e}")
        return None 