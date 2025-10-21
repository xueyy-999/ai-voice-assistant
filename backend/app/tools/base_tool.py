"""
工具插件基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.utils.logger import logger


class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool
    message: str
    data: Any = None
    error: Optional[str] = None


class BaseTool(ABC):
    """工具基类 - 所有工具插件继承此类"""
    
    def __init__(self):
        self.name: str = ""
        self.description: str = ""
        self.parameters: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            ToolResult对象
        """
        pass
    
    def validate_params(self, params: Dict) -> tuple[bool, str]:
        """
        验证参数
        
        Returns:
            (是否有效, 错误信息)
        """
        # 检查必需参数
        required = self.parameters.get("required", [])
        for param in required:
            if param not in params:
                return False, f"缺少必需参数: {param}"
        
        return True, ""
    
    def get_schema(self) -> Dict:
        """
        获取工具schema（用于LLM Function Calling）
        
        Returns:
            符合OpenAI Function格式的schema
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters.get("properties", {}),
                "required": self.parameters.get("required", [])
            }
        }
    
    async def safe_execute(self, **kwargs) -> ToolResult:
        """
        安全执行（带错误处理）
        """
        try:
            # 验证参数
            valid, error = self.validate_params(kwargs)
            if not valid:
                return ToolResult(
                    success=False,
                    message="参数验证失败",
                    error=error
                )
            
            # 执行工具
            logger.info(f"🔧 执行工具: {self.name} with params: {kwargs}")
            result = await self.execute(**kwargs)
            
            if result.success:
                logger.info(f"✅ 工具执行成功: {self.name} - {result.message}")
            else:
                logger.warning(f"⚠️ 工具执行失败: {self.name} - {result.error}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 工具执行异常: {self.name} - {e}")
            return ToolResult(
                success=False,
                message="工具执行异常",
                error=str(e)
            )


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """注册工具"""
        self.tools[tool.name] = tool
        logger.info(f"📝 注册工具: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """获取所有工具"""
        return self.tools
    
    def get_schemas(self) -> list:
        """获取所有工具的schema（用于LLM）"""
        return [tool.get_schema() for tool in self.tools.values()]


# 全局工具注册表
tool_registry = ToolRegistry()

