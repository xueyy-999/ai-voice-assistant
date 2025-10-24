"""
VoicePC Backend - FastAPI应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.utils.logger import logger
from app.api import voice, chat, task, system
from app.database.sqlite_db import init_database

# 导入工具以注册
from app.tools import app_control, file_operation, browser_control
from app.tools import text_processing, media_control, scene_manager
from app.tools.base_tool import tool_registry

# 导入Agent服务以初始化
from app.services.ai.agent_service import agent_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("=" * 60)
    logger.info("🚀 VoicePC Backend starting...")
    logger.info(f"📝 Environment: {settings.APP_ENV}")
    logger.info("=" * 60)
    
    # 初始化数据库
    await init_database()
    logger.info("✅ Database initialized")
    
    # 显示已注册的工具
    tools = tool_registry.get_all_tools()
    logger.info(f"🔧 Registered {len(tools)} tools:")
    for tool_name in tools.keys():
        logger.info(f"   ✓ {tool_name}")
    
    # 显示Agent状态
    if agent_service.agent_executor:
        logger.info("🤖 AI Agent: READY (LangChain)")
    else:
        logger.info("🤖 AI Agent: SIMPLE MODE (需配置API Key)")
    
    logger.info("=" * 60)
    logger.info("✅ VoicePC Backend is ready!")
    logger.info(f"📍 API Docs: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    logger.info("=" * 60)
    
    yield
    
    # 关闭时执行
    logger.info("👋 VoicePC Backend shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title="VoicePC API",
    description="AI语音电脑助手后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS（开发环境完全放开，确保本地调试无阻）
if settings.APP_ENV == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 开发环境允许所有来源
        allow_credentials=False,  # allow_origins=["*"]时必须关闭credentials
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册路由
app.include_router(voice.router, prefix="/api/voice", tags=["语音"])
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])
app.include_router(task.router, prefix="/api/task", tags=["任务"])
app.include_router(system.router, prefix="/api/system", tags=["系统"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "service": "VoicePC Backend",
        "version": "1.0.0",
        "tools_count": len(tool_registry.get_all_tools()),
        "agent_mode": "langchain" if agent_service.agent_executor else "simple"
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "VoicePC API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "tools": "/api/task/tools"
    }


def start_server() -> None:
    """Programmatic server start for scripts."""
    logger.info(f"🌐 Starting server on {settings.APP_HOST}:{settings.APP_PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    start_server()
