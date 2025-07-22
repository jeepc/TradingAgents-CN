# Web工具模块

# 导入用户管理器
from .user_manager import (
    UserManager,
    get_user_manager,
    login_user,
    logout_user,
    check_authentication
)

# 导入MongoDB认证适配器
try:
    from .mongodb_auth_adapter import (
        MongoDBAuthAdapter,
        get_mongodb_auth_adapter
    )
    MONGODB_AUTH_AVAILABLE = True
except ImportError:
    MONGODB_AUTH_AVAILABLE = False

# 导入其他工具模块
from .analysis_runner import *
from .api_checker import *
from .async_progress_tracker import *
from .progress_tracker import *

__all__ = [
    'UserManager',
    'get_user_manager', 
    'login_user',
    'logout_user',
    'check_authentication',
    'MONGODB_AUTH_AVAILABLE'
]

if MONGODB_AUTH_AVAILABLE:
    __all__.extend(['MongoDBAuthAdapter', 'get_mongodb_auth_adapter'])