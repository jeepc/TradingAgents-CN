#!/usr/bin/env python3
"""
认证界面组件
包含登录表单、注册表单等用户界面组件
"""

import streamlit as st
from typing import Dict, Optional
from web.utils.user_manager import get_user_manager, login_user, logout_user, check_authentication

# 导入日志模块
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web_auth_ui')

def render_login_form() -> Dict:
    """渲染登录表单"""
    st.markdown("### 🔐 用户登录")
    
    with st.form("login_form"):
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        
        # 只保留登录按钮
        login_submitted = st.form_submit_button("🚀 登录", use_container_width=True)
    
    result = {
        'action': None,
        'username': username,
        'password': password
    }
    
    if login_submitted:
        if not username or not password:
            st.error("❌ 请填写完整的登录信息")
        else:
            result['action'] = 'login'
    
    return result





def render_user_info_sidebar():
    """在侧边栏渲染用户信息"""
    is_authenticated, username = check_authentication()
    
    if is_authenticated:
        user_manager = get_user_manager()
        user_info = user_manager.get_user_info(username)
        
        if user_info:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 用户信息")
            
            # 用户名
            st.sidebar.text(f"🏷️ {username}")
            
            # 角色
            role = user_info.get('role', 'user')
            role_icon = "👑" if role == "admin" else "👤"
            st.sidebar.text(f"{role_icon} {role}")
            
            # 最后登录时间
            last_login = user_info.get('last_login')
            if last_login:
                from datetime import datetime
                try:
                    login_time = datetime.fromisoformat(last_login)
                    st.sidebar.text(f"🕒 {login_time.strftime('%m-%d %H:%M')}")
                except:
                    pass
            
            # 用户操作按钮
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                if st.button("👤 资料", use_container_width=True):
                    st.session_state['show_user_profile'] = True
                    st.rerun()
            
            with col2:
                if st.button("🚪 登出", use_container_width=True):
                    logout_user()
                    st.success("👋 已成功登出")
                    st.rerun()
    
    else:
        # 未登录状态
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔐 请先登录")
        
        if st.sidebar.button("🚀 立即登录", use_container_width=True):
            st.session_state['show_auth_page'] = True
            st.rerun()


def render_auth_page():
    """渲染认证页面（仅登录）"""
    st.header("🔐 用户登录")
    
    # 检查是否已经登录
    is_authenticated, username = check_authentication()
    
    if is_authenticated:
        st.success(f"✅ 欢迎回来，{username}！")
        st.info("您已经登录成功，可以开始使用股票分析功能。")
        
        if st.button("🔙 返回主页"):
            if 'show_auth_page' in st.session_state:
                del st.session_state['show_auth_page']
            st.rerun()
        
        return
    
    # 渲染登录表单
    login_result = render_login_form()
    
    if login_result['action'] == 'login':
        # 处理登录
        success, message = login_user(login_result['username'], login_result['password'])
        
        if success:
            st.success(message)
            st.info("🔄 正在跳转到主页...")
            
            # 清除认证页面状态
            if 'show_auth_page' in st.session_state:
                del st.session_state['show_auth_page']
            
            # 刷新页面
            st.rerun()
        else:
            st.error(message)
    
    # 显示使用条款
    with st.expander("📋 用户协议和隐私政策"):
        st.markdown("""
        ### 📄 用户协议
        
        1. **账户使用**
           - 每个用户只能注册一个账户
           - 不得分享账户信息给他人使用
           - 保护好您的登录密码
        
        2. **使用规范**
           - 仅用于个人投资研究目的
           - 不得用于商业用途
           - 遵守相关法律法规
        
        3. **数据安全**
           - 我们使用加密技术保护您的密码
           - 不会泄露您的个人信息
           - 定期清理过期会话
        
        ### 🔒 隐私政策
        
        1. **数据收集**
           - 仅收集必要的注册信息
           - 记录使用日志用于系统优化
           - 不收集敏感个人信息
        
        2. **数据使用**
           - 仅用于提供服务
           - 不会向第三方分享
           - 用于改进用户体验
        
        3. **数据保护**
           - 采用行业标准安全措施
           - 定期备份重要数据
           - 提供数据删除选项
        """)


def render_user_profile_page():
    """渲染用户资料页面"""
    # 检查认证
    is_authenticated, username = check_authentication()
    
    if not is_authenticated:
        st.error("⚠️ 请先登录后访问用户资料")
        return
    
    st.header("👤 用户资料")
    
    user_manager = get_user_manager()
    user_info = user_manager.get_user_info(username)
    
    if not user_info:
        st.error("❌ 无法获取用户信息")
        return
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📋 基本信息", "🔐 密码修改", "⚙️ 偏好设置"])
    
    with tab1:
        st.subheader("📋 基本信息")
        
        with st.form("profile_form"):
            new_full_name = st.text_input("姓名", value=user_info.get('full_name', ''))
            new_email = st.text_input("邮箱", value=user_info.get('email', ''))
            
            st.markdown("---")
            st.text(f"用户名: {username}")
            st.text(f"注册时间: {user_info.get('created_at', '未知')[:10]}")
            st.text(f"最后登录: {user_info.get('last_login', '未知')[:16]}")
            st.text(f"账户状态: {'✅ 正常' if user_info.get('is_active', True) else '❌ 禁用'}")
            
            profile_submitted = st.form_submit_button("💾 保存修改")
        
        if profile_submitted:
            updates = {
                'full_name': new_full_name,
                'email': new_email
            }
            
            success, message = user_manager.update_user_info(username, updates)
            
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    with tab2:
        st.subheader("🔐 密码修改")
        
        with st.form("password_form"):
            old_password = st.text_input("当前密码", type="password")
            new_password = st.text_input("新密码", type="password")
            confirm_new_password = st.text_input("确认新密码", type="password")
            
            password_submitted = st.form_submit_button("🔒 修改密码")
        
        if password_submitted:
            if not old_password or not new_password:
                st.error("❌ 请填写完整的密码信息")
            elif new_password != confirm_new_password:
                st.error("❌ 两次输入的新密码不一致")
            else:
                success, message = user_manager.change_password(username, old_password, new_password)
                
                if success:
                    st.success(message)
                    st.info("🔄 请重新登录以确保安全")
                else:
                    st.error(message)
    
    with tab3:
        st.subheader("⚙️ 偏好设置")
        
        preferences = user_info.get('preferences', {})
        
        with st.form("preferences_form"):
            default_market = st.selectbox(
                "默认市场",
                options=["A股", "美股", "港股"],
                index=["A股", "美股", "港股"].index(preferences.get('default_market', 'A股'))
            )
            
            auto_refresh = st.checkbox(
                "自动刷新分析进度",
                value=preferences.get('auto_refresh', True)
            )
            
            theme = st.selectbox(
                "界面主题",
                options=["default", "dark", "light"],
                index=["default", "dark", "light"].index(preferences.get('theme', 'default'))
            )
            
            preferences_submitted = st.form_submit_button("💾 保存偏好")
        
        if preferences_submitted:
            new_preferences = {
                'default_market': default_market,
                'auto_refresh': auto_refresh,
                'theme': theme
            }
            
            updates = {'preferences': new_preferences}
            success, message = user_manager.update_user_info(username, updates)
            
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    # 返回按钮
    if st.button("🔙 返回主页"):
        if 'show_user_profile' in st.session_state:
            del st.session_state['show_user_profile']
        st.rerun()


def render_admin_user_management():
    """渲染管理员用户管理页面"""
    # 检查认证和权限
    is_authenticated, username = check_authentication()
    
    if not is_authenticated:
        st.error("⚠️ 请先登录")
        return
    
    user_manager = get_user_manager()
    user_info = user_manager.get_user_info(username)
    
    if not user_info or user_info.get('role') != 'admin':
        st.error("⚠️ 您没有管理员权限")
        return
    
    st.header("👑 用户管理")
    
    # 用户统计
    stats = user_manager.get_user_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总用户数", stats['total_users'])
    
    with col2:
        st.metric("活跃会话", stats['active_sessions'])
    
    with col3:
        st.metric("总会话数", stats['total_sessions'])
    
    # 清理过期会话按钮
    if st.button("🧹 清理过期会话"):
        user_manager.cleanup_expired_sessions()
        st.success("✅ 过期会话已清理")
        st.rerun()
    
    # 用户列表（简化版，仅显示基本信息）
    st.subheader("📝 用户列表")
    st.info("用户管理功能正在开发中...")


def check_auth_requirements() -> bool:
    """检查是否需要显示认证页面"""
    # 这里可以配置哪些功能需要登录
    # 目前设置为可选登录
    return False


def require_auth_for_analysis() -> bool:
    """检查股票分析是否需要登录"""
    # 可以通过环境变量或配置文件控制
    import os
    return os.getenv('REQUIRE_LOGIN_FOR_ANALYSIS', 'false').lower() == 'true' 