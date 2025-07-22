import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,

    # MongoDB用户认证默认配置
    "mongodb_auth": {
        "enabled": True,  # 启用MongoDB认证存储
        "host": "localhost",
        "port": 27017,
        "username": "admin",
        "password": "Trade123456",
        "database": "tradingagents",
        "auth_source": "admin",
        "collections": {
            "users": "auth_users",
            "sessions": "auth_sessions"
        }
    },

    # 用户认证系统配置
    "user_auth": {
        "default_admin_username": "admin",
        "default_admin_password": "Trade123456",
        "session_expire_hours": 24,
        "min_password_length": 6,
        "require_login_for_analysis": True,  # 默认启用登录要求
        "password_hash_algorithm": "sha256"
    },

    # Note: Database and cache configuration is now managed by .env file and config.database_manager
    # No database/cache settings in default config to avoid configuration conflicts
}
