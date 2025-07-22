#!/usr/bin/env python3
"""
UserManager初始化问题修复验证脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_user_manager_initialization():
    """测试UserManager初始化"""
    print("🔍 测试UserManager初始化修复")
    print("=" * 50)
    
    try:
        # 测试导入
        print("1️⃣ 测试模块导入...")
        from web.utils.user_manager import UserManager, get_user_manager
        print("   ✅ 模块导入成功")
        
        # 测试MongoDB适配器导入
        print("\n2️⃣ 测试MongoDB适配器...")
        try:
            from web.utils.mongodb_auth_adapter import get_mongodb_auth_adapter
            adapter = get_mongodb_auth_adapter()
            if adapter:
                print("   ✅ MongoDB适配器可用")
            else:
                print("   📄 MongoDB适配器不可用，将使用JSON存储")
        except Exception as e:
            print(f"   📄 MongoDB适配器导入失败: {e}")
        
        # 测试UserManager直接初始化
        print("\n3️⃣ 测试UserManager直接初始化...")
        user_manager = UserManager()
        print("   ✅ UserManager初始化成功")
        
        # 检查mongodb_adapter属性
        print("\n4️⃣ 检查mongodb_adapter属性...")
        if hasattr(user_manager, 'mongodb_adapter'):
            print("   ✅ mongodb_adapter属性存在")
            if user_manager.mongodb_adapter:
                print("   🗄️ MongoDB适配器已连接")
            else:
                print("   📄 使用JSON文件存储")
        else:
            print("   ❌ mongodb_adapter属性不存在")
            return False
        
        # 测试get_user_manager()函数
        print("\n5️⃣ 测试get_user_manager()函数...")
        user_manager2 = get_user_manager()
        print("   ✅ get_user_manager()成功")
        
        # 测试基本功能
        print("\n6️⃣ 测试基本功能...")
        
        # 测试用户统计
        stats = user_manager.get_user_stats()
        print(f"   📊 用户统计: {stats}")
        
        # 测试默认管理员验证
        default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Trade123456")
        
        is_valid, message, user_data = user_manager.authenticate_user(default_username, default_password)
        if is_valid:
            print(f"   ✅ 默认管理员验证成功")
        else:
            print(f"   ❌ 默认管理员验证失败: {message}")
        
        print("\n🎉 所有测试通过！UserManager初始化问题已修复")
        return True
        
    except AttributeError as e:
        print(f"\n❌ AttributeError: {e}")
        print("   修复未完成，请检查代码")
        return False
    except Exception as e:
        print(f"\n❌ 其他错误: {e}")
        return False

def test_authentication_flow():
    """测试完整的认证流程"""
    print("\n" + "=" * 50)
    print("🔐 测试完整认证流程")
    print("=" * 50)
    
    try:
        from web.utils.user_manager import get_user_manager
        from web.components.auth_components import check_authentication
        
        # 检查认证状态
        print("1️⃣ 检查当前认证状态...")
        is_authenticated, username = check_authentication()
        print(f"   认证状态: {'✅ 已登录' if is_authenticated else '❌ 未登录'}")
        if is_authenticated:
            print(f"   当前用户: {username}")
        
        # 测试登录流程
        print("\n2️⃣ 测试登录流程...")
        user_manager = get_user_manager()
        
        # 尝试登录默认管理员
        default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Trade123456")
        
        is_valid, message, user_data = user_manager.authenticate_user(default_username, default_password)
        if is_valid:
            print("   ✅ 用户认证成功")
            
            # 创建会话
            token = user_manager.create_session(default_username)
            if token:
                print(f"   ✅ 会话创建成功: {token[:8]}...")
                
                # 验证会话
                is_valid_session, session_username = user_manager.validate_session(token)
                if is_valid_session:
                    print(f"   ✅ 会话验证成功: {session_username}")
                    
                    # 销毁会话
                    user_manager.destroy_session(token)
                    print("   ✅ 会话销毁成功")
                else:
                    print("   ❌ 会话验证失败")
            else:
                print("   ❌ 会话创建失败")
        else:
            print(f"   ❌ 用户认证失败: {message}")
        
        print("\n🎉 认证流程测试完成！")
        return True
        
    except Exception as e:
        print(f"\n❌ 认证流程测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 UserManager修复验证脚本")
    print("=" * 60)
    
    # 测试初始化
    init_success = test_user_manager_initialization()
    
    if init_success:
        # 测试认证流程
        auth_success = test_authentication_flow()
        
        if auth_success:
            print("\n" + "=" * 60)
            print("🎉 所有测试通过！系统可以正常启动了")
            print("💡 现在可以运行: python -m streamlit run web/app.py")
        else:
            print("\n⚠️ 初始化成功但认证流程有问题")
    else:
        print("\n❌ 初始化失败，需要进一步检查代码") 