"""
文件操作工具
"""
import os
from pathlib import Path
from typing import List
from app.tools.base_tool import BaseTool, ToolResult
from app.adapters.windows_api import windows_api
from app.utils.logger import logger


class FileOperationTool(BaseTool):
    """文件操作工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "file_operation"
        self.description = "文件和文件夹操作，包括创建、打开、搜索、删除等"
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["open", "create", "search", "delete", "exists"],
                    "description": "操作类型"
                },
                "path": {
                    "type": "string",
                    "description": "文件或文件夹路径"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容（用于create操作）"
                },
                "query": {
                    "type": "string",
                    "description": "搜索关键词（用于search操作）"
                }
            },
            "required": ["action"]
        }
        
        # 安全限制：禁止操作这些目录
        self.forbidden_paths = [
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)"
        ]
    
    async def execute(self, action: str, path: str = None, content: str = None, 
                     query: str = None, **kwargs) -> ToolResult:
        """执行文件操作"""
        try:
            if action == "open":
                return await self._open_file(path)
            elif action == "create":
                return await self._create_file(path, content)
            elif action == "search":
                return await self._search_files(query, path)
            elif action == "delete":
                return await self._delete_file(path)
            elif action == "exists":
                return await self._check_exists(path)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的操作: {action}",
                    error="Invalid action"
                )
        
        except Exception as e:
            logger.error(f"文件操作失败: {e}")
            return ToolResult(
                success=False,
                message="文件操作失败",
                error=str(e)
            )
    
    def _is_safe_path(self, path: str) -> bool:
        """检查路径是否安全"""
        if not path:
            return False
        
        abs_path = os.path.abspath(path)
        for forbidden in self.forbidden_paths:
            if abs_path.startswith(forbidden):
                return False
        return True
    
    async def _open_file(self, path: str) -> ToolResult:
        """打开文件"""
        if not path:
            return ToolResult(success=False, message="未指定文件路径", error="No path")
        
        if not os.path.exists(path):
            return ToolResult(
                success=False,
                message=f"文件不存在: {path}",
                error="File not found"
            )
        
        if windows_api.open_file(path):
            return ToolResult(
                success=True,
                message=f"已打开文件: {path}",
                data={"path": path}
            )
        else:
            return ToolResult(
                success=False,
                message=f"打开文件失败: {path}",
                error="Failed to open"
            )
    
    async def _create_file(self, path: str, content: str = None) -> ToolResult:
        """创建文件或文件夹"""
        if not path:
            return ToolResult(success=False, message="未指定路径", error="No path")
        
        if not self._is_safe_path(path):
            return ToolResult(
                success=False,
                message="禁止在系统目录创建文件",
                error="Forbidden path"
            )
        
        try:
            # 判断是文件还是文件夹
            if path.endswith('/') or path.endswith('\\') or '.' not in os.path.basename(path):
                # 创建文件夹
                os.makedirs(path, exist_ok=True)
                return ToolResult(
                    success=True,
                    message=f"已创建文件夹: {path}",
                    data={"path": path, "type": "directory"}
                )
            else:
                # 创建文件
                dir_path = os.path.dirname(path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                
                with open(path, 'w', encoding='utf-8') as f:
                    if content:
                        f.write(content)
                
                return ToolResult(
                    success=True,
                    message=f"已创建文件: {path}",
                    data={"path": path, "type": "file"}
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"创建失败: {e}",
                error=str(e)
            )
    
    async def _search_files(self, query: str, search_path: str = None) -> ToolResult:
        """搜索文件"""
        if not query:
            return ToolResult(success=False, message="未指定搜索关键词", error="No query")
        
        search_path = search_path or os.path.expanduser("~\\Desktop")
        
        if not os.path.exists(search_path):
            return ToolResult(
                success=False,
                message=f"搜索路径不存在: {search_path}",
                error="Path not found"
            )
        
        try:
            found_files = []
            for root, dirs, files in os.walk(search_path):
                # 限制搜索深度
                if root.count(os.sep) - search_path.count(os.sep) > 3:
                    continue
                
                for file in files:
                    if query.lower() in file.lower():
                        file_path = os.path.join(root, file)
                        found_files.append(file_path)
                        
                        # 限制结果数量
                        if len(found_files) >= 20:
                            break
                
                if len(found_files) >= 20:
                    break
            
            return ToolResult(
                success=True,
                message=f"找到 {len(found_files)} 个文件",
                data={"files": found_files, "query": query}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"搜索失败: {e}",
                error=str(e)
            )
    
    async def _delete_file(self, path: str) -> ToolResult:
        """删除文件（谨慎操作）"""
        if not path:
            return ToolResult(success=False, message="未指定路径", error="No path")
        
        if not self._is_safe_path(path):
            return ToolResult(
                success=False,
                message="禁止删除系统目录文件",
                error="Forbidden path"
            )
        
        # 出于安全考虑，暂不实现删除功能
        return ToolResult(
            success=False,
            message="删除操作需要用户确认，当前不支持自动删除",
            error="Delete not allowed"
        )
    
    async def _check_exists(self, path: str) -> ToolResult:
        """检查文件是否存在"""
        if not path:
            return ToolResult(success=False, message="未指定路径", error="No path")
        
        exists = os.path.exists(path)
        is_file = os.path.isfile(path) if exists else False
        is_dir = os.path.isdir(path) if exists else False
        
        return ToolResult(
            success=True,
            message=f"{'存在' if exists else '不存在'}: {path}",
            data={
                "exists": exists,
                "is_file": is_file,
                "is_directory": is_dir,
                "path": path
            }
        )


# 创建实例并注册
from app.tools.base_tool import tool_registry
file_operation_tool = FileOperationTool()
tool_registry.register(file_operation_tool)

