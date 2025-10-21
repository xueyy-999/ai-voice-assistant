"""
LangChain Agent核心服务
"""
from typing import Dict, List, Any, Optional
from app.config import settings
from app.utils.logger import logger
from app.tools.base_tool import tool_registry
from app.services.ai.llm_client import llm_client


class AgentService:
    """AI Agent服务"""
    
    def __init__(self):
        self.agent_executor = None
        self.tools_list = []
        self._init_agent()
    
    def _init_agent(self):
        """初始化Agent"""
        try:
            # 如果没有配置API Key，使用简化版
            if not settings.DEEPSEEK_API_KEY:
                logger.warning("⚠️ 未配置API Key，Agent使用简化模式")
                self.agent_executor = None
                return
            
            # 延迟导入LangChain相关依赖，避免无Key时强依赖（便于无编译环境运行）
            from langchain.agents import AgentExecutor, create_openai_functions_agent
            from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
            from langchain_openai import ChatOpenAI
            # Tool 仅用于运行期注册，无需类型标注强约束

            # 获取所有工具
            self.tools_list = self._create_langchain_tools()
            
            # 创建LLM
            llm = ChatOpenAI(
                base_url=settings.DEEPSEEK_BASE_URL,
                api_key=settings.DEEPSEEK_API_KEY,
                model=settings.DEEPSEEK_MODEL,
                temperature=0.7
            )
            
            # 创建提示词模板
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是VoicePC智能助手，帮助用户通过语音控制Windows电脑。

你可以使用以下工具来完成用户的请求：
- app_control: 控制应用程序（打开、关闭）
- file_operation: 文件操作（创建、打开、搜索）
- browser_control: 浏览器控制（打开网页、搜索）
- text_processing: 文本处理（创建文档）
- media_control: 多媒体控制（音量、播放音乐）
- scene_manager: 场景管理（执行复杂场景）

请根据用户的指令，选择合适的工具来完成任务。
如果任务需要多个步骤，请逐步执行。
执行完成后，用简洁友好的语言总结结果。"""),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # 创建Agent
            agent = create_openai_functions_agent(llm, self.tools_list, prompt)
            
            # 创建AgentExecutor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools_list,
                verbose=True,
                max_iterations=5,
                return_intermediate_steps=True
            )
            
            logger.info(f"✅ Agent初始化成功，加载了 {len(self.tools_list)} 个工具")
            
        except Exception as e:
            logger.error(f"❌ Agent初始化失败: {e}")
            self.agent_executor = None
    
    def _create_langchain_tools(self) -> List[Any]:
        """将VoicePC工具转换为LangChain Tool格式"""
        from langchain.tools import Tool
        langchain_tools: List[Any] = []
        
        for tool_name, tool in tool_registry.get_all_tools().items():
            # 创建工具的执行函数
            async def tool_func(**kwargs):
                result = await tool.safe_execute(**kwargs)
                if result.success:
                    return f"成功: {result.message}"
                else:
                    return f"失败: {result.error}"
            
            # 创建LangChain Tool
            lc_tool = Tool(
                name=tool.name,
                description=tool.description,
                func=tool_func,
                coroutine=tool_func  # 支持异步
            )
            
            langchain_tools.append(lc_tool)
        
        return langchain_tools
    
    async def execute(self, user_input: str, chat_history: List = None) -> Dict:
        """
        执行Agent任务
        
        Args:
            user_input: 用户输入
            chat_history: 对话历史
            
        Returns:
            {
                "output": "最终输出",
                "intermediate_steps": [{"tool": "", "result": ""}],
                "success": True/False
            }
        """
        try:
            # 如果Agent未初始化，使用简化版
            if not self.agent_executor:
                return await self._execute_simple(user_input)
            
            logger.info(f"🤖 Agent开始执行: {user_input}")
            
            # 执行Agent
            result = await self.agent_executor.ainvoke({
                "input": user_input,
                "chat_history": chat_history or []
            })
            
            # 提取结果
            output = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # 格式化中间步骤
            steps = []
            for step in intermediate_steps:
                action, observation = step
                steps.append({
                    "tool": action.tool,
                    "tool_input": action.tool_input,
                    "result": observation
                })
            
            logger.info(f"✅ Agent执行完成: {len(steps)} 步")
            
            return {
                "output": output,
                "intermediate_steps": steps,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Agent执行失败: {e}")
            return {
                "output": f"执行失败: {e}",
                "intermediate_steps": [],
                "success": False
            }
    
    async def _execute_simple(self, user_input: str) -> Dict:
        """简化版执行（不使用LangChain）"""
        from app.services.ai.intent_parser import intent_parser
        
        logger.info("📋 使用简化模式执行")
        
        # 解析意图
        intent = await intent_parser.parse(user_input)
        
        # 映射意图到工具
        tool_mapping = {
            "app_control": "app_control",
            "file_operation": "file_operation",
            "browser_control": "browser_control",
            "text_processing": "text_processing",
            "media_control": "media_control",
            "scene": "scene_manager"
        }
        
        tool_name = tool_mapping.get(intent.type)
        if not tool_name:
            return {
                "output": "抱歉，我不知道如何处理这个请求",
                "intermediate_steps": [],
                "success": False
            }
        
        # 获取工具
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            return {
                "output": "工具不可用",
                "intermediate_steps": [],
                "success": False
            }
        
        # 执行工具
        params = {"action": intent.action}
        params.update(intent.entities)
        
        # 特殊处理场景工具
        if tool_name == "scene_manager":
            scene_mapping = {
                "prepare_work": "prepare_work",
                "create_mode": "create_mode",
                "study_mode": "study_mode",
                "relax_mode": "relax_mode"
            }
            params = {"scene_name": scene_mapping.get(intent.action, "prepare_work")}
        
        result = await tool.safe_execute(**params)
        
        steps = [{
            "tool": tool_name,
            "tool_input": params,
            "result": result.message
        }]
        
        return {
            "output": result.message,
            "intermediate_steps": steps,
            "success": result.success
        }


# 全局实例
agent_service = AgentService()

