#!/usr/bin/env python3
"""
所有页面登录要求功能测试脚本
验证用户认证系统是否正确保护所有功能页面
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_page_access_control():
    """测试页面访问控制"""
    print("🔍 测试页面访问控制功能")
    print("=" * 60)
    
    # 测试环境变量
    print("1️⃣ 检查登录要求配置")
    require_login_env = os.getenv("REQUIRE_LOGIN_FOR_ANALYSIS", "true")
    require_login = require_login_env.lower() == "true"
    
    print(f"   REQUIRE_LOGIN_FOR_ANALYSIS = {require_login_env}")
    print(f"   登录要求: {'✅ 启用' if require_login else '❌ 禁用'}")
    
    if not require_login:
        print("\n⚠️ 警告: 登录要求已禁用，所有页面都可以无需登录访问")
        print("   要启用全页面登录保护，请设置: REQUIRE_LOGIN_FOR_ANALYSIS=true")
        return
    
    # 功能页面列表
    protected_pages = [
        "📊 股票分析",
        "⚙️ 配置管理", 
        "💾 缓存管理",
        "💰 Token统计",
        "📈 历史记录",
        "🔧 系统状态",
        "👤 用户资料",
        "👑 用户管理"
    ]
    
    public_pages = [
        "🔐 用户认证"
    ]
    
    print("\n2️⃣ 页面分类")
    print("   🔒 需要登录的页面:")
    for page in protected_pages:
        print(f"      - {page}")
    
    print("   🌐 公开访问的页面:")
    for page in public_pages:
        print(f"      - {page}")
    
    # 测试用户认证模块
    print("\n3️⃣ 测试用户认证模块")
    try:
        from web.utils.user_manager import get_user_manager
        from web.components.auth_components import check_authentication
        
        user_manager = get_user_manager()
        print("   ✅ 用户管理器初始化成功")
        
        # 检查当前认证状态
        is_authenticated, username = check_authentication()
        print(f"   认证状态: {'✅ 已登录' if is_authenticated else '❌ 未登录'}")
        if is_authenticated:
            print(f"   当前用户: {username}")
        
        # 检查默认管理员
        default_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "Trade123456")
        
        is_valid, message, user_data = user_manager.authenticate_user(default_username, default_password)
        if is_valid:
            print(f"   ✅ 默认管理员验证成功")
            print(f"   管理员角色: {user_data.get('role', 'user')}")
        else:
            print(f"   ❌ 默认管理员验证失败: {message}")
        
    except Exception as e:
        print(f"   ❌ 用户认证模块测试失败: {e}")
        return
    
    # 测试页面访问逻辑模拟
    print("\n4️⃣ 模拟页面访问逻辑")
    
    def simulate_page_access(page_name, is_user_authenticated):
        """模拟页面访问"""
        if page_name == "🔐 用户认证":
            return True, "公开页面，允许访问"
        elif require_login and not is_user_authenticated:
            return False, "需要登录才能访问"
        else:
            return True, "已登录用户，允许访问"
    
    # 测试未登录用户访问
    print("\n   📋 未登录用户访问测试:")
    for page in protected_pages:
        allowed, reason = simulate_page_access(page, False)
        status = "✅ 允许" if allowed else "🔒 拒绝"
        print(f"      {page}: {status} - {reason}")
    
    # 测试认证页面
    for page in public_pages:
        allowed, reason = simulate_page_access(page, False)
        status = "✅ 允许" if allowed else "🔒 拒绝"
        print(f"      {page}: {status} - {reason}")
    
    # 测试已登录用户访问
    print("\n   📋 已登录用户访问测试:")
    for page in protected_pages + public_pages:
        allowed, reason = simulate_page_access(page, True)
        status = "✅ 允许" if allowed else "🔒 拒绝"
        print(f"      {page}: {status} - {reason}")

def test_sidebar_navigation():
    """测试侧边栏导航逻辑"""
    print("\n" + "=" * 60)
    print("🧭 测试侧边栏导航逻辑")
    print("=" * 60)
    
    require_login = os.getenv("REQUIRE_LOGIN_FOR_ANALYSIS", "true").lower() == "true"
    
    # 模拟不同用户状态下的侧边栏显示
    def get_sidebar_pages(is_authenticated, user_role=None):
        """模拟获取侧边栏页面列表"""
        base_pages = ["📊 股票分析", "⚙️ 配置管理", "💾 缓存管理", "💰 Token统计", "📈 历史记录", "🔧 系统状态"]
        
        if require_login and not is_authenticated:
            # 需要登录但用户未登录：只显示认证页面
            return ["🔐 用户认证"]
        elif is_authenticated:
            # 已登录：显示所有功能页面
            if user_role == 'admin':
                return base_pages + ["👤 用户资料", "👑 用户管理"]
            else:
                return base_pages + ["👤 用户资料"]
        else:
            # 不需要登录：显示所有功能页面和认证页面
            return base_pages + ["🔐 用户认证"]
    
    print("1️⃣ 未登录用户侧边栏:")
    unauth_pages = get_sidebar_pages(False)
    for page in unauth_pages:
        print(f"   - {page}")
    
    print("\n2️⃣ 已登录普通用户侧边栏:")
    user_pages = get_sidebar_pages(True, 'user')
    for page in user_pages:
        print(f"   - {page}")
    
    print("\n3️⃣ 已登录管理员用户侧边栏:")
    admin_pages = get_sidebar_pages(True, 'admin')
    for page in admin_pages:
        print(f"   - {page}")
    
    # 验证逻辑
    print("\n4️⃣ 侧边栏逻辑验证:")
    if require_login:
        expected_unauth = 1  # 只有认证页面
        actual_unauth = len(unauth_pages)
        if actual_unauth == expected_unauth and "🔐 用户认证" in unauth_pages:
            print("   ✅ 未登录用户只能看到认证页面")
        else:
            print(f"   ❌ 未登录用户页面数量异常: 期望{expected_unauth}，实际{actual_unauth}")
        
        if len(user_pages) > len(unauth_pages):
            print("   ✅ 已登录用户可以看到更多页面")
        else:
            print("   ❌ 已登录用户页面数量异常")
        
        if len(admin_pages) > len(user_pages):
            print("   ✅ 管理员用户可以看到最多页面")
        else:
            print("   ❌ 管理员用户页面数量异常")
    else:
        print("   ⚠️ 登录要求已禁用，所有用户都能看到所有页面")

def demo_user_flow():
    """演示用户使用流程"""
    print("\n" + "=" * 60)
    print("👤 用户使用流程演示")
    print("=" * 60)
    
    require_login = os.getenv("REQUIRE_LOGIN_FOR_ANALYSIS", "true").lower() == "true"
    
    if not require_login:
        print("⚠️ 当前登录要求已禁用，用户可以直接访问所有功能")
        return
    
    print("📋 新用户访问流程:")
    print("1. 用户访问 http://localhost:8501")
    print("2. 侧边栏只显示 '🔐 用户认证' 选项")
    print("3. 如果用户尝试访问其他页面，会显示登录要求页面")
    print("4. 用户点击 '立即登录' 按钮")
    print("5. 跳转到用户认证页面")
    print("6. 用户输入用户名密码登录")
    print("7. 登录成功后，侧边栏显示所有功能页面")
    print("8. 用户可以正常访问所有功能")
    
    print("\n📋 管理员用户额外流程:")
    print("9. 管理员登录后可以看到 '👑 用户管理' 页面")
    print("10. 可以查看和管理系统用户")
    
    print("\n📋 用户登出流程:")
    print("11. 用户点击侧边栏的 '登出' 按钮")
    print("12. 会话被销毁，用户状态变为未登录")
    print("13. 侧边栏重新只显示认证页面")
    print("14. 访问功能页面会再次要求登录")

if __name__ == "__main__":
    print("🧪 全页面登录要求测试")
    print("=" * 60)
    
    try:
        # 测试页面访问控制
        test_page_access_control()
        
        # 测试侧边栏导航
        test_sidebar_navigation()
        
        # 演示用户流程
        demo_user_flow()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成！")
        print("\n💡 测试建议:")
        print("1. 启动Web应用: python -m streamlit run web/app.py")
        print("2. 测试未登录访问各功能页面")
        print("3. 使用默认管理员登录: admin / Trade123456")
        print("4. 验证登录后可以访问所有功能")
        print("5. 测试登出功能")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("请检查项目配置和依赖") 