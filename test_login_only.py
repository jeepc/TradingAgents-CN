#!/usr/bin/env python3
"""
仅登录功能测试脚本
验证去掉注册功能后的登录页面是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_login_only_functionality():
    """测试仅登录功能"""
    print("🔍 测试仅登录功能")
    print("=" * 50)
    
    try:
        # 测试认证组件导入
        print("1️⃣ 测试认证组件导入...")
        from web.components.auth_components import render_auth_page, render_login_form
        print("   ✅ 认证组件导入成功")
        
        # 测试用户管理器
        print("\n2️⃣ 测试用户管理器...")
        from web.utils.user_manager import get_user_manager, check_authentication
        user_manager = get_user_manager()
        print("   ✅ 用户管理器初始化成功")
        
        # 检查默认管理员
        print("\n3️⃣ 验证默认管理员账户...")
        default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Trade123456")
        
        print(f"   默认用户名: {default_username}")
        print(f"   默认密码: {default_password}")
        
        # 验证登录
        is_valid, message, user_data = user_manager.authenticate_user(default_username, default_password)
        if is_valid:
            print("   ✅ 默认管理员验证成功")
            print(f"   用户角色: {user_data.get('role', 'user')}")
        else:
            print(f"   ❌ 默认管理员验证失败: {message}")
        
        # 检查当前认证状态
        print("\n4️⃣ 检查当前认证状态...")
        is_authenticated, username = check_authentication()
        print(f"   认证状态: {'✅ 已登录' if is_authenticated else '❌ 未登录'}")
        if is_authenticated:
            print(f"   当前用户: {username}")
        
        # 测试用户统计
        print("\n5️⃣ 测试用户统计...")
        stats = user_manager.get_user_stats()
        print(f"   注册用户数: {stats.get('total_users', 0)}")
        print(f"   活跃会话数: {stats.get('active_sessions', 0)}")
        print(f"   存储方式: {'MongoDB' if user_manager.mongodb_adapter else 'JSON文件'}")
        
        print("\n🎉 仅登录功能测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

def verify_no_registration():
    """验证注册功能已被移除"""
    print("\n" + "=" * 50)
    print("🚫 验证注册功能已移除")
    print("=" * 50)
    
    try:
        # 检查是否还有注册相关的函数
        from web.components.auth_components import render_register_form
        print("   ⚠️ 注册表单函数仍然存在")
        has_register_form = True
    except ImportError:
        print("   ✅ 注册表单函数已移除")
        has_register_form = False
    
    # 检查登录表单是否还有注册按钮
    print("\n检查登录表单结构...")
    import inspect
    from web.components.auth_components import render_login_form
    
    # 获取函数源码
    source = inspect.getsource(render_login_form)
    
    if "注册" in source or "register" in source.lower():
        print("   ⚠️ 登录表单中仍包含注册相关内容")
        has_register_content = True
    else:
        print("   ✅ 登录表单中已移除注册相关内容")
        has_register_content = False
    
    # 总结
    if not has_register_form and not has_register_content:
        print("\n🎉 注册功能已完全移除！")
        return True
    else:
        print("\n⚠️ 注册功能移除不完整，请检查代码")
        return False

def demo_login_flow():
    """演示仅登录的用户流程"""
    print("\n" + "=" * 50)
    print("🎯 仅登录模式用户流程")
    print("=" * 50)
    
    print("📋 用户访问流程:")
    print("1. 用户访问 http://localhost:8501")
    print("2. 未登录用户看到登录页面")
    print("3. 页面显示默认管理员账户信息")
    print("4. 用户输入用户名和密码")
    print("5. 点击 '🚀 登录' 按钮")
    print("6. 登录成功后跳转到主页")
    print("7. 可以访问所有功能页面")
    
    print("\n📋 简化的界面特点:")
    print("✅ 只有登录表单，没有注册选项")
    print("✅ 直接显示默认管理员账户信息")
    print("✅ 界面更简洁，专注于登录功能")
    print("✅ 不需要处理注册验证逻辑")
    
    print("\n📋 默认管理员账户:")
    default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Trade123456")
    print(f"   用户名: {default_username}")
    print(f"   密码: {default_password}")
    
    print("\n💡 测试建议:")
    print("1. 启动Web应用: python -m streamlit run web/app.py")
    print("2. 访问任何功能页面，应该直接跳转到登录页")
    print("3. 使用默认管理员账户登录")
    print("4. 验证登录后可以正常使用所有功能")

if __name__ == "__main__":
    print("🧪 仅登录功能测试")
    print("=" * 60)
    
    try:
        # 测试基本功能
        basic_test = test_login_only_functionality()
        
        # 验证注册功能移除
        register_removed = verify_no_registration()
        
        # 演示用户流程
        demo_login_flow()
        
        print("\n" + "=" * 60)
        if basic_test and register_removed:
            print("🎉 所有测试通过！仅登录功能正常工作")
        else:
            print("⚠️ 部分测试未通过，请检查代码")
        
        print("\n🚀 现在可以启动Web应用测试登录功能了！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("请检查项目配置和依赖") 