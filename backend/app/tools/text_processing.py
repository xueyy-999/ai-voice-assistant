"""
文本处理工具
"""
import os
from datetime import datetime
from app.tools.base_tool import BaseTool, ToolResult
from app.adapters.windows_api import windows_api
from app.utils.logger import logger


class TextProcessingTool(BaseTool):
    """文本处理工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "text_processing"
        self.description = "文本处理，包括创建文档、写入内容等"
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create_document", "write_text", "open_notepad"],
                    "description": "操作类型"
                },
                "title": {
                    "type": "string",
                    "description": "文档标题"
                },
                "content": {
                    "type": "string",
                    "description": "文档内容"
                },
                "format": {
                    "type": "string",
                    "enum": ["txt", "md"],
                    "description": "文档格式，默认txt"
                }
            },
            "required": ["action"]
        }
    
    async def execute(self, action: str, title: str = None, content: str = None,
                     format: str = "txt", **kwargs) -> ToolResult:
        """执行文本处理操作"""
        try:
            if action == "create_document":
                return await self._create_document(title, content, format)
            elif action == "write_text":
                return await self._write_text(content)
            elif action == "open_notepad":
                return await self._open_notepad()
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的操作: {action}",
                    error="Invalid action"
                )
        
        except Exception as e:
            logger.error(f"文本处理失败: {e}")
            return ToolResult(
                success=False,
                message="文本处理失败",
                error=str(e)
            )
    
    async def _create_document(self, title: str, content: str, format: str = "txt") -> ToolResult:
        """创建文档"""
        try:
            # 生成文件名
            if not title:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                title = f"document_{timestamp}"
            
            # 清理文件名
            title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            
            # 生成文件路径（桌面）
            desktop = os.path.expanduser("~/Desktop")
            filename = f"{title}.{format}"
            filepath = os.path.join(desktop, filename)
            
            # 写入内容
            with open(filepath, 'w', encoding='utf-8') as f:
                if content:
                    f.write(content)
                else:
                    f.write(f"# {title}\n\n")
            
            # 打开文件
            windows_api.open_file(filepath)
            
            return ToolResult(
                success=True,
                message=f"已创建并打开文档: {filename}",
                data={
                    "path": filepath,
                    "title": title,
                    "format": format
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"创建文档失败: {e}",
                error=str(e)
            )
    
    async def _write_text(self, content: str) -> ToolResult:
        """写入文本（到剪贴板）"""
        if not content:
            return ToolResult(
                success=False,
                message="未指定内容",
                error="No content"
            )
        
        try:
            import pyperclip
            pyperclip.copy(content)
            
            return ToolResult(
                success=True,
                message="文本已复制到剪贴板，可以粘贴使用",
                data={"content": content[:100] + "..." if len(content) > 100 else content}
            )
        
        except ImportError:
            # 降级：创建临时文件
            return await self._create_document("temp", content, "txt")
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"写入文本失败: {e}",
                error=str(e)
            )
    
    async def _open_notepad(self) -> ToolResult:
        """打开记事本"""
        app_path = windows_api.find_app_path("notepad")
        if app_path:
            pid = windows_api.start_process(app_path)
            if pid:
                return ToolResult(
                    success=True,
                    message="已打开记事本",
                    data={"pid": pid}
                )
        
        return ToolResult(
            success=False,
            message="打开记事本失败",
            error="Failed to open notepad"
        )


# 创建实例并注册
from app.tools.base_tool import tool_registry
text_processing_tool = TextProcessingTool()
tool_registry.register(text_processing_tool)

