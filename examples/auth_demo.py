#!/usr/bin/env python3
"""
登录功能演示脚本
展示如何使用用户认证系统
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
from web.utils.user_manager import get_user_manager, UserManager

def demo_user_registration():
    """演示用户注册功能"""
    print("🎯 用户注册功能演示")
    print("=" * 50)
    
    user_manager = get_user_manager()
    
    # 演示注册新用户
    test_users = [
        {
            'username': 'demo_user',
            'email': 'demo@example.com',
            'password': 'demo123',
            'full_name': '演示用户'
        },
        {
            'username': 'admin_user',
            'email': 'admin@example.com',
            'password': 'admin123',
            'full_name': '管理员'
        }
    ]
    
    for user_data in test_users:
        print(f"\n📝 注册用户: {user_data['username']}")
        
        success, message = user_manager.register_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            full_name=user_data['full_name']
        )
        
        if success:
            print(f"   ✅ {message}")
            
            # 如果是管理员用户，设置为admin角色
            if user_data['username'] == 'admin_user':
                users = user_manager._load_users()
                users[user_data['username']]['role'] = 'admin'
                user_manager._save_users(users)
                print(f"   👑 已设置为管理员角色")
        else:
            print(f"   ❌ {message}")

def demo_user_authentication():
    """演示用户认证功能"""
    print("\n🔐 用户认证功能演示")
    print("=" * 50)
    
    user_manager = get_user_manager()
    
    # 测试用户登录
    test_logins = [
        {'username': 'demo_user', 'password': 'demo123'},
        {'username': 'demo_user', 'password': 'wrong_password'},
        {'username': 'nonexistent_user', 'password': 'any_password'},
        {'username': 'admin_user', 'password': 'admin123'},
    ]
    
    for login_data in test_logins:
        print(f"\n🔍 测试登录: {login_data['username']}")
        
        is_valid, message, user_data = user_manager.authenticate_user(
            username=login_data['username'],
            password=login_data['password']
        )
        
        if is_valid:
            print(f"   ✅ {message}")
            print(f"   👤 用户信息: {user_data.get('full_name', 'N/A')}")
            print(f"   📧 邮箱: {user_data.get('email', 'N/A')}")
            print(f"   👑 角色: {user_data.get('role', 'user')}")
        else:
            print(f"   ❌ {message}")

def demo_session_management():
    """演示会话管理功能"""
    print("\n🔑 会话管理功能演示")
    print("=" * 50)
    
    user_manager = get_user_manager()
    
    # 为用户创建会话
    username = 'demo_user'
    print(f"\n📝 为用户 {username} 创建会话...")
    
    token = user_manager.create_session(username)
    if token:
        print(f"   ✅ 会话创建成功: {token[:16]}...")
        
        # 验证会话
        print(f"\n🔍 验证会话令牌...")
        is_valid, session_username = user_manager.validate_session(token)
        
        if is_valid:
            print(f"   ✅ 会话有效，用户: {session_username}")
        else:
            print(f"   ❌ 会话无效")
        
        # 销毁会话
        print(f"\n🗑️ 销毁会话...")
        user_manager.destroy_session(token)
        
        # 再次验证（应该无效）
        is_valid, _ = user_manager.validate_session(token)
        print(f"   {'❌ 会话已失效' if not is_valid else '⚠️ 会话仍然有效'}")
    else:
        print(f"   ❌ 会话创建失败")

def demo_user_management():
    """演示用户信息管理功能"""
    print("\n👤 用户信息管理演示")
    print("=" * 50)
    
    user_manager = get_user_manager()
    username = 'demo_user'
    
    # 获取用户信息
    print(f"\n📋 获取用户信息: {username}")
    user_info = user_manager.get_user_info(username)
    
    if user_info:
        print(f"   ✅ 用户信息获取成功:")
        print(f"   📧 邮箱: {user_info.get('email', 'N/A')}")
        print(f"   🏷️ 姓名: {user_info.get('full_name', 'N/A')}")
        print(f"   📅 注册时间: {user_info.get('created_at', 'N/A')[:19]}")
        print(f"   🕒 最后登录: {user_info.get('last_login', 'N/A')[:19] if user_info.get('last_login') else 'N/A'}")
        print(f"   🔧 偏好设置: {user_info.get('preferences', {})}")
    else:
        print(f"   ❌ 用户信息获取失败")
    
    # 更新用户信息
    print(f"\n✏️ 更新用户信息...")
    
    updates = {
        'full_name': '演示用户 (已更新)',
        'preferences': {
            'theme': 'dark',
            'default_market': '美股',
            'auto_refresh': False
        }
    }
    
    success, message = user_manager.update_user_info(username, updates)
    
    if success:
        print(f"   ✅ {message}")
        
        # 再次获取用户信息验证更新
        updated_info = user_manager.get_user_info(username)
        if updated_info:
            print(f"   📝 更新后姓名: {updated_info.get('full_name', 'N/A')}")
            print(f"   🎨 主题偏好: {updated_info.get('preferences', {}).get('theme', 'N/A')}")
    else:
        print(f"   ❌ {message}")

def demo_password_management():
    """演示密码管理功能"""
    print("\n🔒 密码管理功能演示")
    print("=" * 50)
    
    user_manager = get_user_manager()
    username = 'demo_user'
    
    # 测试密码修改
    print(f"\n🔐 测试密码修改: {username}")
    
    # 错误的当前密码
    print(f"\n❌ 使用错误的当前密码...")
    success, message = user_manager.change_password(username, 'wrong_password', 'new_demo123')
    print(f"   {'✅' if success else '❌'} {message}")
    
    # 弱密码
    print(f"\n❌ 使用弱密码...")
    success, message = user_manager.change_password(username, 'demo123', '123')
    print(f"   {'✅' if success else '❌'} {message}")
    
    # 正确的密码修改
    print(f"\n✅ 正确的密码修改...")
    success, message = user_manager.change_password(username, 'demo123', 'new_demo123')
    print(f"   {'✅' if success else '❌'} {message}")
    
    if success:
        # 验证新密码
        print(f"\n🔍 验证新密码...")
        is_valid, auth_message, _ = user_manager.authenticate_user(username, 'new_demo123')
        print(f"   {'✅' if is_valid else '❌'} 新密码验证: {auth_message}")

def demo_system_statistics():
    """演示系统统计功能"""
    print("\n📊 系统统计功能演示")
    print("=" * 50)
    
    user_manager = get_user_manager()
    
    # 获取用户统计
    stats = user_manager.get_user_stats()
    
    print(f"\n📈 系统统计信息:")
    print(f"   👥 总用户数: {stats['total_users']}")
    print(f"   🔑 活跃会话: {stats['active_sessions']}")
    print(f"   📋 总会话数: {stats['total_sessions']}")
    
    # 清理过期会话
    print(f"\n🧹 清理过期会话...")
    user_manager.cleanup_expired_sessions()
    
    # 再次获取统计
    stats_after = user_manager.get_user_stats()
    print(f"   📊 清理后活跃会话: {stats_after['active_sessions']}")
    print(f"   📊 清理后总会话数: {stats_after['total_sessions']}")

def cleanup_demo_data():
    """清理演示数据"""
    print("\n🧹 清理演示数据")
    print("=" * 50)
    
    user_manager = get_user_manager()
    
    # 删除演示用户数据文件
    try:
        if user_manager.users_file.exists():
            user_manager.users_file.unlink()
            print("   ✅ 删除用户数据文件")
        
        if user_manager.sessions_file.exists():
            user_manager.sessions_file.unlink()
            print("   ✅ 删除会话数据文件")
        
        print("   🎉 演示数据清理完成")
    except Exception as e:
        print(f"   ❌ 清理失败: {e}")

def main():
    """主函数"""
    print("🔐 TradingAgents-CN 登录功能演示")
    print("=" * 80)
    
    try:
        # 1. 用户注册演示
        demo_user_registration()
        
        # 2. 用户认证演示
        demo_user_authentication()
        
        # 3. 会话管理演示
        demo_session_management()
        
        # 4. 用户信息管理演示
        demo_user_management()
        
        # 5. 密码管理演示
        demo_password_management()
        
        # 6. 系统统计演示
        demo_system_statistics()
        
        print("\n" + "=" * 80)
        print("🎉 登录功能演示完成！")
        
        # 询问是否清理演示数据
        print("\n💡 演示说明:")
        print("   1. 用户数据存储在 web/data/ 目录")
        print("   2. 密码使用SHA-256哈希加密")
        print("   3. 会话令牌支持自动过期")
        print("   4. 支持用户偏好设置和角色管理")
        print("   5. 管理员可以管理所有用户")
        
        print("\n🚀 使用建议:")
        print("   1. 启动Web界面: python -m streamlit run web/app.py")
        print("   2. 点击侧边栏的'🚀 立即登录'按钮")
        print("   3. 使用演示账户登录:")
        print("      - 普通用户: demo_user / new_demo123")
        print("      - 管理员: admin_user / admin123")
        print("   4. 体验用户资料管理和偏好设置")
        
        # 询问是否清理数据
        response = input("\n🗑️ 是否清理演示数据？(y/N): ").strip().lower()
        if response in ['y', 'yes']:
            cleanup_demo_data()
        else:
            print("   📄 演示数据已保留，可继续在Web界面中测试")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 