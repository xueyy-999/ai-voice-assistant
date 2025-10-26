"""
大模型客户端 - DeepSeek/通义千问
"""
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from app.config import settings
from app.utils.logger import logger
import aiohttp


class LLMClient:
    """大模型客户端"""
    
    def __init__(self):
        self.provider = "deepseek"
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化客户端"""
        try:
            def _normalize_url(url: str) -> str:
                if not url:
                    return url
                u = url.strip()
                # 修正常见粘贴错误：中文逗号/英文逗号/空格
                u = u.replace('，', ',').replace(' ', '')
                u = u.replace(',', '.')
                # 去掉重复的斜杠
                while '//' in u[8:]:
                    u = u.replace('//', '/').replace(':/', '://')
                return u

            base_url = _normalize_url(settings.DEEPSEEK_BASE_URL)
            if settings.DEEPSEEK_API_KEY:
                self.client = AsyncOpenAI(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url=base_url
                )
                safe_key = settings.DEEPSEEK_API_KEY[:6] + "***"
                logger.info(f"✅ LLM初始化成功 provider=ark base_url={base_url} model={settings.DEEPSEEK_MODEL} key={safe_key}")
            else:
                logger.warning("⚠️ 未配置DEEPSEEK_API_KEY，LLM功能将使用模拟模式")
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            self.client = None
    
    async def chat_with_messages(self,
                                 messages: List[Dict[str, str]],
                                 temperature: float = 0.7,
                                 max_tokens: int = 2000) -> Optional[str]:
        """
        对话接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            temperature: 温度（0-1）
            max_tokens: 最大token数
            
        Returns:
            AI回复文本
        """
        try:
            if not self.client:
                # 没有SDK客户端，尝试HTTP直连
                http_reply = await self._chat_via_http(messages, temperature, max_tokens)
                if http_reply:
                    return http_reply
                return await self._chat_fallback(messages)
            
            response = await self.client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            reply = response.choices[0].message.content
            logger.info(f"✅ LLM回复成功 (tokens: {response.usage.total_tokens})")
            
            return reply
            
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            # SDK失败时，尝试HTTP直连
            http_reply = await self._chat_via_http(messages, temperature, max_tokens)
            if http_reply:
                return http_reply
            return await self._chat_fallback(messages)
    
    async def chat_with_functions(self,
                                  messages: List[Dict[str, str]],
                                  functions: List[Dict],
                                  function_call: str = "auto") -> Optional[Dict]:
        """
        带Function Calling的对话
        
        Args:
            messages: 消息列表
            functions: 可用函数列表
            function_call: 函数调用策略
            
        Returns:
            {"reply": "文本", "function_call": {...}} 或 None
        """
        try:
            if not self.client:
                return await self._chat_fallback(messages)
            
            response = await self.client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=messages,
                functions=functions,
                function_call=function_call,
                temperature=0.7
            )
            
            choice = response.choices[0]
            
            result = {
                "reply": choice.message.content,
                "function_call": None
            }
            
            if choice.message.function_call:
                result["function_call"] = {
                    "name": choice.message.function_call.name,
                    "arguments": choice.message.function_call.arguments
                }
                logger.info(f"🔧 Function Call: {result['function_call']['name']}")
            
            return result
            
        except Exception as e:
            logger.error(f"LLM Function Calling失败: {e}")
            return None
    
    async def _chat_fallback(self, messages: List[Dict[str, str]]) -> str:
        """降级方案：简单规则引擎"""
        user_message = messages[-1]["content"] if messages else ""
        
        # 简单的规则匹配
        if "打开" in user_message:
            return "好的，我将为您打开应用程序。"
        elif "搜索" in user_message or "查找" in user_message:
            return "好的，我将为您搜索相关内容。"
        elif "播放" in user_message:
            return "好的，我将为您播放音乐。"
        elif "创建" in user_message or "新建" in user_message:
            return "好的，我将为您创建文件。"
        elif "关闭" in user_message:
            return "好的，我将关闭应用。"
        elif "准备工作" in user_message:
            return "好的，我将为您准备工作环境：打开开发工具、浏览器和播放背景音乐。"
        else:
            return "我理解了，让我来帮您处理。"

    async def _chat_via_http(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Optional[str]:
        """直接通过HTTP调用 OpenAI兼容接口，避免SDK兼容问题。"""
        if not settings.DEEPSEEK_API_KEY or not settings.DEEPSEEK_BASE_URL:
            return None
        base_url = settings.DEEPSEEK_BASE_URL.strip().replace('，', ',').replace(' ', '').replace(',', '.')
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    text = await resp.text()
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data["choices"][0]["message"]["content"]
                        logger.info("✅ HTTP直连LLM成功")
                        return reply
                    logger.error(f"LLM HTTP错误 {resp.status}: {text}")
                    return None
        except Exception as e:
            logger.error(f"LLM HTTP直连失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """检查LLM是否可用"""
        return self.client is not None
    
    async def chat(self, user_input: str) -> str:
        """简单的聊天接口"""
        messages = [
            {"role": "system", "content": "你是VoicePC智能助手，可以帮助用户控制电脑和回答问题。"},
            {"role": "user", "content": user_input}
        ]
        return await self.chat_with_messages(messages)


# 全局实例
llm_client = LLMClient()

