"""
浏览器控制工具
"""
from app.tools.base_tool import BaseTool, ToolResult
from app.adapters.windows_api import windows_api
from app.utils.logger import logger


class BrowserControlTool(BaseTool):
    """浏览器控制工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "browser_control"
        self.description = "控制浏览器，打开网页、搜索内容等"
        self.parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["open", "search"],
                    "description": "操作类型：open=打开URL，search=搜索内容"
                },
                "url": {
                    "type": "string",
                    "description": "要打开的网址（用于open操作）"
                },
                "query": {
                    "type": "string",
                    "description": "搜索关键词（用于search操作）"
                },
                "engine": {
                    "type": "string",
                    "enum": ["baidu", "google", "bing"],
                    "description": "搜索引擎，默认baidu"
                }
            },
            "required": ["action"]
        }
        
        self.search_engines = {
            "baidu": "https://www.baidu.com/s?wd={}",
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}"
        }
    
    async def execute(self, action: str, url: str = None, query: str = None,
                     engine: str = "baidu", **kwargs) -> ToolResult:
        """执行浏览器操作"""
        try:
            if action == "open":
                return await self._open_url(url)
            elif action == "search":
                return await self._search(query, engine)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的操作: {action}",
                    error="Invalid action"
                )
        
        except Exception as e:
            logger.error(f"浏览器操作失败: {e}")
            return ToolResult(
                success=False,
                message="浏览器操作失败",
                error=str(e)
            )
    
    async def _open_url(self, url: str) -> ToolResult:
        """打开URL"""
        if not url:
            return ToolResult(
                success=False,
                message="未指定URL",
                error="No URL provided"
            )
        
        # 补全协议
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        if windows_api.open_url(url):
            return ToolResult(
                success=True,
                message=f"已在浏览器中打开: {url}",
                data={"url": url}
            )
        else:
            return ToolResult(
                success=False,
                message=f"打开URL失败: {url}",
                error="Failed to open URL"
            )
    
    async def _search(self, query: str, engine: str = "baidu") -> ToolResult:
        """搜索内容"""
        if not query:
            return ToolResult(
                success=False,
                message="未指定搜索关键词",
                error="No query provided"
            )
        
        # 获取搜索引擎URL
        search_url_template = self.search_engines.get(engine, self.search_engines["baidu"])
        
        # 构建搜索URL
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        search_url = search_url_template.format(encoded_query)
        
        if windows_api.open_url(search_url):
            return ToolResult(
                success=True,
                message=f"已使用{engine}搜索: {query}",
                data={
                    "query": query,
                    "engine": engine,
                    "url": search_url
                }
            )
        else:
            return ToolResult(
                success=False,
                message=f"搜索失败: {query}",
                error="Failed to search"
            )


# 创建实例并注册
from app.tools.base_tool import tool_registry
browser_control_tool = BrowserControlTool()
tool_registry.register(browser_control_tool)

