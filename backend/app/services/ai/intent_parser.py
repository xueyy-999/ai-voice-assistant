"""
意图解析器 - 自然语言理解
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.utils.logger import logger
from app.services.ai.llm_client import llm_client


class Intent(BaseModel):
    """意图对象"""
    type: str  # app_control, file_operation, browser_control, text_processing, media_control, scene
    action: str  # open, close, create, search, play, etc.
    entities: Dict[str, Any] = {}
    confidence: float = 0.0
    raw_text: str = ""


class IntentParser:
    """意图解析器"""
    
    def __init__(self):
        self.intent_patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """加载意图模式"""
        return {
            "app_control": {
                "keywords": ["打开", "启动", "关闭", "切换", "最小化"],
                "actions": {
                    "打开": "open",
                    "启动": "open",
                    "关闭": "close",
                    "切换": "switch",
                    "最小化": "minimize"
                }
            },
            "file_operation": {
                "keywords": ["创建", "新建", "删除", "移动", "复制", "搜索文件", "查找文件", "打开文件"],
                "actions": {
                    "创建": "create",
                    "新建": "create",
                    "删除": "delete",
                    "移动": "move",
                    "复制": "copy",
                    "搜索": "search",
                    "查找": "search",
                    "打开文件": "open"
                }
            },
            "browser_control": {
                "keywords": ["搜索", "打开网页", "访问", "浏览"],
                "actions": {
                    "搜索": "search",
                    "打开网页": "open",
                    "访问": "open",
                    "浏览": "open"
                }
            },
            "text_processing": {
                "keywords": ["写", "编辑", "记录", "写入", "生成文档"],
                "actions": {
                    "写": "write",
                    "编辑": "edit",
                    "记录": "write",
                    "写入": "write",
                    "生成文档": "create_document"
                }
            },
            "media_control": {
                "keywords": ["播放", "暂停", "音量", "调节", "截图"],
                "actions": {
                    "播放": "play",
                    "暂停": "pause",
                    "音量": "volume",
                    "调节": "adjust",
                    "截图": "screenshot"
                }
            },
            "scene": {
                "keywords": ["准备工作", "创作模式", "开始工作", "工作模式", "学习模式"],
                "actions": {
                    "准备工作": "prepare_work",
                    "创作模式": "create_mode",
                    "开始工作": "prepare_work",
                    "工作模式": "work_mode",
                    "学习模式": "study_mode"
                }
            },
            "system_query": {
                "keywords": ["几点", "时间", "日期", "今天", "现在", "星期"],
                "actions": {
                    "几点": "get_time",
                    "时间": "get_time",
                    "日期": "get_date",
                    "今天": "get_date",
                    "现在": "get_time",
                    "星期": "get_date"
                }
            }
        }
    
    async def parse(self, text: str) -> Intent:
        """
        解析用户输入的意图
        
        Args:
            text: 用户输入文本
            
        Returns:
            Intent对象
        """
        try:
            # 首先尝试规则匹配（快速）
            intent = self._rule_based_parse(text)
            
            # 如果规则匹配置信度低，使用LLM增强
            if intent.confidence < 0.8 and llm_client.is_available():
                intent = await self._llm_based_parse(text, intent)
            
            logger.info(f"🎯 意图解析: {intent.type}/{intent.action} (置信度: {intent.confidence:.2f})")
            
            return intent
            
        except Exception as e:
            logger.error(f"意图解析失败: {e}")
            return Intent(
                type="unknown",
                action="unknown",
                raw_text=text,
                confidence=0.0
            )
    
    def _rule_based_parse(self, text: str) -> Intent:
        """基于规则的意图识别"""
        text_lower = text.lower()
        
        # 遍历所有意图类型
        for intent_type, config in self.intent_patterns.items():
            for keyword, action in config["actions"].items():
                if keyword in text:
                    # 提取实体
                    entities = self._extract_entities(text, intent_type, keyword)
                    
                    return Intent(
                        type=intent_type,
                        action=action,
                        entities=entities,
                        confidence=0.85,
                        raw_text=text
                    )
        
        # 未匹配到
        return Intent(
            type="unknown",
            action="unknown",
            raw_text=text,
            confidence=0.3
        )
    
    def _extract_entities(self, text: str, intent_type: str, keyword: str) -> Dict[str, Any]:
        """提取实体"""
        entities = {}
        
        # 移除关键词，剩余的可能是实体
        remaining = text.replace(keyword, "").strip()
        
        if intent_type == "app_control":
            # 提取应用名称
            entities["app_name"] = remaining if remaining else "未知应用"
        
        elif intent_type == "file_operation":
            # 提取文件名或路径
            entities["file_name"] = remaining if remaining else "新文件"
        
        elif intent_type == "browser_control":
            # 提取搜索关键词或URL
            if "http" in remaining or "www" in remaining:
                entities["url"] = remaining
            else:
                entities["query"] = remaining if remaining else ""
        
        elif intent_type == "text_processing":
            # 提取内容
            entities["content"] = remaining
        
        elif intent_type == "media_control":
            # 提取媒体信息
            if "音量" in text:
                # 尝试提取数字
                import re
                numbers = re.findall(r'\d+', text)
                if numbers:
                    entities["volume"] = int(numbers[0])
            entities["media_type"] = remaining if remaining else "音乐"
        
        elif intent_type == "scene":
            entities["scene_name"] = keyword
        
        return entities
    
    async def _llm_based_parse(self, text: str, fallback_intent: Intent) -> Intent:
        """使用LLM增强意图识别"""
        try:
            prompt = f"""
分析以下用户指令，返回JSON格式的意图信息：

用户指令：{text}

请按以下格式返回：
{{
    "type": "意图类型（app_control/file_operation/browser_control/text_processing/media_control/scene）",
    "action": "具体动作（open/close/create/search等）",
    "entities": {{
        "key": "value"
    }},
    "confidence": 0.95
}}

只返回JSON，不要其他内容。
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await llm_client.chat(messages, temperature=0.3)
            
            if response:
                import json
                # 尝试解析JSON
                intent_data = json.loads(response)
                return Intent(
                    type=intent_data.get("type", fallback_intent.type),
                    action=intent_data.get("action", fallback_intent.action),
                    entities=intent_data.get("entities", fallback_intent.entities),
                    confidence=intent_data.get("confidence", 0.9),
                    raw_text=text
                )
            
        except Exception as e:
            logger.warning(f"LLM意图增强失败: {e}")
        
        return fallback_intent


# 全局实例
intent_parser = IntentParser()

