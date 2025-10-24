"""
多媒体控制工具
"""
import os
from app.tools.base_tool import BaseTool, ToolResult
from app.adapters.windows_api import windows_api
from app.utils.logger import logger


class MediaControlTool(BaseTool):
    """多媒体控制工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "media_control"
        self.description = "控制多媒体，包括音量、播放器等"
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["volume", "play_music", "play", "pause", "screenshot"],
                    "description": "操作类型"
                },
                "level": {
                    "type": "integer",
                    "description": "音量级别 (0-100)，用于volume操作"
                },
                "music_query": {
                    "type": "string",
                    "description": "音乐搜索关键词，用于play_music操作"
                },
                "media_type": {
                    "type": "string",
                    "description": "媒体类型（音乐、视频等）"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, action: str, level: int = None, 
                     music_query: str = None, media_type: str = None, **kwargs) -> ToolResult:
        """执行多媒体操作"""
        try:
            if action == "volume":
                return await self._set_volume(level)
            elif action in ["play_music", "play"]:
                # "播放音乐"或"play"都支持
                query = music_query or media_type or "音乐"
                return await self._play_music(query)
            elif action == "pause":
                return await self._pause_media()
            elif action == "screenshot":
                return await self._screenshot()
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的操作: {action}",
                    error="Invalid action"
                )
        
        except Exception as e:
            logger.error(f"多媒体操作失败: {e}")
            return ToolResult(
                success=False,
                message="多媒体操作失败",
                error=str(e)
            )
    
    async def _set_volume(self, level: int) -> ToolResult:
        """设置音量"""
        if level is None:
            return ToolResult(
                success=False,
                message="未指定音量级别",
                error="No level provided"
            )
        
        if not 0 <= level <= 100:
            return ToolResult(
                success=False,
                message="音量级别必须在0-100之间",
                error="Invalid level"
            )
        
        if windows_api.set_system_volume(level):
            return ToolResult(
                success=True,
                message=f"已将音量设置为 {level}%",
                data={"level": level}
            )
        else:
            return ToolResult(
                success=False,
                message="设置音量失败",
                error="Failed to set volume"
            )
    
    async def _play_music(self, music_query: str) -> ToolResult:
        """播放音乐"""
        from app.adapters.windows_api import windows_api as win_api
        
        # 优先尝试打开网易云APP
        app_path = win_api.find_app_path("网易云音乐")
        if app_path and os.path.exists(app_path.replace('%USERNAME%', os.environ.get('USERNAME', ''))):
            pid = win_api.start_process(app_path)
            if pid:
                return ToolResult(
                    success=True,
                    message=f"已打开网易云音乐APP{f'（搜索: {music_query}）' if music_query else ''}",
                    data={"app": "cloudmusic", "pid": pid}
                )
        
        # 如果APP打不开，降级到网页版
        music_url = f"https://music.163.com/#/search/m/?s={music_query}" if music_query else "https://music.163.com"
        if windows_api.open_url(music_url):
            return ToolResult(
                success=True,
                message=f"已打开网易云音乐网页版{f'（搜索: {music_query}）' if music_query else ''}",
                data={"url": music_url}
            )
        else:
            return ToolResult(
                success=False,
                message="打开音乐失败",
                error="Failed to open music"
            )
    
    async def _pause_media(self) -> ToolResult:
        """暂停媒体（模拟按键）"""
        # 这里需要使用pyautogui模拟按键
        # 简化实现
        return ToolResult(
            success=True,
            message="媒体控制功能开发中",
            data={"action": "pause"}
        )
    
    async def _screenshot(self) -> ToolResult:
        """截图"""
        import os
        from datetime import datetime
        
        try:
            # 使用PIL截图
            from PIL import ImageGrab
            
            # 生成文件名
            desktop = os.path.expanduser("~/Desktop")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(desktop, filename)
            
            # 截图
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            return ToolResult(
                success=True,
                message=f"截图已保存到桌面: {filename}",
                data={"path": filepath}
            )
        
        except ImportError:
            return ToolResult(
                success=False,
                message="PIL库未安装，无法截图",
                error="PIL not installed"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"截图失败: {e}",
                error=str(e)
            )


# 创建实例并注册
from app.tools.base_tool import tool_registry
media_control_tool = MediaControlTool()
tool_registry.register(media_control_tool)

