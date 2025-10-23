"""
系统相关API
"""
from fastapi import APIRouter
from pydantic import BaseModel
import platform
import psutil

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    健康检查
    """
    return {
        "status": "ok",
        "message": "VoicePC Backend is running"
    }


class ConfigRequest(BaseModel):
    """配置请求"""
    key: str
    value: str


@router.get("/info")
async def get_system_info():
    """
    获取系统信息
    """
    return {
        "os": platform.system(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "capabilities": [
            "app_control",
            "file_operation",
            "browser_control",
            "text_processing",
            "media_control"
        ]
    }


@router.get("/apps")
async def get_installed_apps():
    """
    获取已安装应用列表
    """
    # TODO: 实现应用列表获取
    return {
        "apps": [
            {"name": "微信", "path": "C:\\Program Files\\Tencent\\WeChat\\WeChat.exe"},
            {"name": "Chrome", "path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"}
        ]
    }


@router.post("/config")
async def update_config(request: ConfigRequest):
    """
    更新配置
    """
    # TODO: 实现配置更新
    return {
        "success": True
    }

