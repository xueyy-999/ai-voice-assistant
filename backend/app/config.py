"""
配置管理
"""
from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # DeepSeek/通义千问（DashScope OpenAI兼容）
    # 从 .env 读取，默认留空，避免使用无效占位Key导致降级
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DEEPSEEK_MODEL: str = "qwen-turbo"
    
    # 阿里云语音配置
    ALI_APPKEY: str = ""
    ALI_ACCESS_KEY: str = ""
    ALI_SECRET_KEY: str = ""
    
    # 应用配置
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/voicepc.log"
    
    # 数据库配置
    DATABASE_PATH: str = "data/voicepc.db"
    
    # 安全配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:*",
        "http://127.0.0.1:*",
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # 忽略额外字段


# 创建全局配置实例
settings = Settings()

# 确保必要的目录存在
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

