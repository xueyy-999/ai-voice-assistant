"""
应用控制工具
"""
from app.tools.base_tool import BaseTool, ToolResult
from app.adapters.windows_api import windows_api
from app.utils.logger import logger


class AppControlTool(BaseTool):
    """应用程序控制工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "app_control"
        self.description = "控制Windows应用程序，包括打开、关闭、切换等操作"
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["open", "close", "check"],
                    "description": "操作类型：open=打开应用，close=关闭应用，check=检查是否运行"
                },
                "app_name": {
                    "type": "string",
                    "description": "应用程序名称，如：微信、Chrome、VS Code等"
                }
            },
            "required": ["action", "app_name"]
        }
    
    async def execute(self, action: str, app_name: str, **kwargs) -> ToolResult:
        """
        执行应用控制操作
        
        Args:
            action: 操作类型（open/close/check）
            app_name: 应用名称
        """
        try:
            if action == "open":
                return await self._open_app(app_name)
            elif action == "close":
                return await self._close_app(app_name)
            elif action == "check":
                return await self._check_app(app_name)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的操作: {action}",
                    error="Invalid action"
                )
        
        except Exception as e:
            logger.error(f"应用控制失败: {e}")
            return ToolResult(
                success=False,
                message="应用控制失败",
                error=str(e)
            )
    
    async def _open_app(self, app_name: str) -> ToolResult:
        """打开应用"""
        # 查找应用路径
        app_path = windows_api.find_app_path(app_name)
        if not app_path:
            return ToolResult(
                success=False,
                message=f"未找到应用: {app_name}",
                error="App not found"
            )
        
        # 检查是否已经运行
        process_name = app_path.split('\\')[-1] if '\\' in app_path else app_path
        if windows_api.is_process_running(process_name):
            return ToolResult(
                success=True,
                message=f"{app_name} 已经在运行",
                data={"status": "already_running"}
            )
        
        # 启动应用
        pid = windows_api.start_process(app_path)
        if pid:
            return ToolResult(
                success=True,
                message=f"已成功打开 {app_name}",
                data={"pid": pid, "app_path": app_path}
            )
        else:
            return ToolResult(
                success=False,
                message=f"打开 {app_name} 失败",
                error="Failed to start process"
            )
    
    async def _close_app(self, app_name: str) -> ToolResult:
        """关闭应用"""
        # 查找应用路径
        app_path = windows_api.find_app_path(app_name)
        if not app_path:
            return ToolResult(
                success=False,
                message=f"未找到应用: {app_name}",
                error="App not found"
            )
        
        # 获取进程名
        process_name = app_path.split('\\')[-1] if '\\' in app_path else app_path
        
        # 检查是否运行
        if not windows_api.is_process_running(process_name):
            return ToolResult(
                success=True,
                message=f"{app_name} 未在运行",
                data={"status": "not_running"}
            )
        
        # 结束进程
        if windows_api.kill_process_by_name(process_name):
            return ToolResult(
                success=True,
                message=f"已成功关闭 {app_name}",
                data={"process_name": process_name}
            )
        else:
            return ToolResult(
                success=False,
                message=f"关闭 {app_name} 失败",
                error="Failed to kill process"
            )
    
    async def _check_app(self, app_name: str) -> ToolResult:
        """检查应用状态"""
        app_path = windows_api.find_app_path(app_name)
        if not app_path:
            return ToolResult(
                success=False,
                message=f"未找到应用: {app_name}",
                error="App not found"
            )
        
        process_name = app_path.split('\\')[-1] if '\\' in app_path else app_path
        processes = windows_api.find_process_by_name(process_name)
        
        is_running = len(processes) > 0
        
        return ToolResult(
            success=True,
            message=f"{app_name} {'正在运行' if is_running else '未运行'}",
            data={
                "is_running": is_running,
                "processes": processes
            }
        )


# 创建实例并注册
from app.tools.base_tool import tool_registry
app_control_tool = AppControlTool()
tool_registry.register(app_control_tool)

