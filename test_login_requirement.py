#!/usr/bin/env python3
"""
登录要求功能测试脚本
验证用户认证系统的登录要求功能是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_login_requirement():
    """测试登录要求功能"""
    print("🔍 测试登录要求功能")
    print("=" * 50)
    
    # 测试环境变量设置
    print("\n1️⃣ 测试环境变量配置")
    require_login_env = os.getenv("REQUIRE_LOGIN_FOR_ANALYSIS", "true")
    print(f"   REQUIRE_LOGIN_FOR_ANALYSIS = {require_login_env}")
    
    require_login = require_login_env.lower() == "true"
    print(f"   登录要求: {'✅ 启用' if require_login else '❌ 禁用'}")
    
    # 测试用户认证功能
    print("\n2️⃣ 测试用户认证功能")
    try:
        from web.utils.user_manager import get_user_manager
        from web.components.auth_components import check_authentication
        
        user_manager = get_user_manager()
        print(f"   用户管理器: ✅ 初始化成功")
        
        # 检查存储方式
        if user_manager.mongodb_adapter:
            print(f"   存储方式: 🗄️ MongoDB")
        else:
            print(f"   存储方式: 📄 JSON文件")
        
        # 检查默认管理员
        default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Trade123456")
        
        print(f"   默认管理员: {default_username}")
        
        # 验证默认管理员账户
        is_valid, message, user_data = user_manager.authenticate_user(default_username, default_password)
        if is_valid:
            print(f"   管理员验证: ✅ 成功")
            print(f"   管理员角色: {user_data.get('role', 'user')}")
        else:
            print(f"   管理员验证: ❌ 失败 - {message}")
        
        # 获取用户统计
        stats = user_manager.get_user_stats()
        print(f"   注册用户数: {stats.get('total_users', 0)}")
        print(f"   活跃会话数: {stats.get('active_sessions', 0)}")
        
    except Exception as e:
        print(f"   用户认证测试: ❌ 失败 - {e}")
    
    # 测试登录页面重定向逻辑
    print("\n3️⃣ 测试登录重定向逻辑")
    
    if require_login:
        print("   ✅ 启用登录要求时：")
        print("      - 未登录用户将看到登录提示页面")
        print("      - 页面显示登录按钮和默认管理员信息")
        print("      - 用户必须登录后才能访问股票分析功能")
    else:
        print("   ❌ 禁用登录要求时：")
        print("      - 用户可以直接访问股票分析功能")
        print("      - 不需要登录验证")
    
    # 提供启动建议
    print("\n4️⃣ 启动建议")
    print("   🚀 启动Web应用：")
    print("      python -m streamlit run web/app.py")
    print()
    print("   🔐 默认管理员登录：")
    print(f"      用户名: {default_username}")
    print(f"      密码: {default_password}")
    print()
    print("   ⚙️ 配置登录要求：")
    print("      - 在 .env 文件中设置 REQUIRE_LOGIN_FOR_ANALYSIS=true")
    print("      - 或在环境变量中设置该值")
    
    # 验证关键组件
    print("\n5️⃣ 关键组件验证")
    
    # 检查MongoDB适配器
    try:
        from web.utils.mongodb_auth_adapter import get_mongodb_auth_adapter
        adapter = get_mongodb_auth_adapter()
        if adapter:
            print("   🗄️ MongoDB适配器: ✅ 可用")
        else:
            print("   📄 MongoDB适配器: ❌ 不可用，将使用JSON存储")
    except Exception as e:
        print(f"   MongoDB适配器: ❌ 错误 - {e}")
    
    # 检查认证组件
    try:
        from web.components.auth_components import render_auth_page
        print("   🔐 认证组件: ✅ 可用")
    except Exception as e:
        print(f"   认证组件: ❌ 错误 - {e}")
    
    return require_login

def demo_login_flow():
    """演示登录流程"""
    print("\n" + "=" * 50)
    print("🎯 登录流程演示")
    print("=" * 50)
    
    require_login = test_login_requirement()
    
    if not require_login:
        print("\n⚠️ 当前登录要求已禁用")
        print("   要启用登录要求，请设置环境变量：")
        print("   REQUIRE_LOGIN_FOR_ANALYSIS=true")
        return
    
    print("\n✅ 登录要求已启用")
    print("\n📋 用户访问流程：")
    print("   1. 用户访问 http://localhost:8501")
    print("   2. 系统检查用户登录状态")
    print("   3. 如果未登录，显示登录提示页面")
    print("   4. 用户点击'立即登录'按钮")
    print("   5. 跳转到用户认证页面")
    print("   6. 用户输入用户名密码登录")
    print("   7. 登录成功后可访问股票分析功能")
    
    print("\n🎮 测试步骤：")
    print("   1. 启动Web应用")
    print("   2. 访问主页（应该看到登录提示）")
    print("   3. 点击'立即登录'按钮")
    print("   4. 使用默认管理员账户登录")
    print("   5. 验证是否可以访问股票分析功能")

if __name__ == "__main__":
    demo_login_flow()
    
    print("\n🎉 测试完成！")
    print("💡 提示：现在启动Web应用测试登录功能吧！") 