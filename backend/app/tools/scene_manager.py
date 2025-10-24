"""
场景管理工具 - 复杂场景编排
"""
import json
import os
from typing import List, Dict
from app.tools.base_tool import BaseTool, ToolResult, tool_registry
from app.utils.logger import logger


class SceneManagerTool(BaseTool):
    """场景管理工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "scene_manager"
        self.description = "执行预定义的复杂场景，如'准备工作'、'创作模式'等"
        self.parameters = {
            "type": "object",
            "properties": {
                "scene_name": {
                    "type": "string",
                    "enum": ["prepare_work", "create_mode", "study_mode", "relax_mode"],
                    "description": "场景名称"
                }
            },
            "required": ["scene_name"]
        }
        
        # 预定义场景
        self.scenes = self._load_scenes()
    
    def _load_scenes(self) -> Dict:
        """加载预定义场景"""
        return {
            "prepare_work": {
                "name": "准备工作",
                "description": "准备开始工作：打开记事本、浏览器和音乐",
                "steps": [
                    {
                        "tool": "app_control",
                        "params": {"action": "open", "app_name": "记事本"},
                        "description": "打开记事本"
                    },
                    {
                        "tool": "browser_control",
                        "params": {"action": "open", "url": "https://www.baidu.com"},
                        "description": "打开百度"
                    },
                    {
                        "tool": "media_control",
                        "params": {"action": "play_music", "music_query": "轻音乐"},
                        "description": "播放轻音乐"
                    },
                    {
                        "tool": "media_control",
                        "params": {"action": "volume", "level": 30},
                        "description": "设置音量为30%"
                    }
                ]
            },
            "create_mode": {
                "name": "创作模式",
                "description": "准备创作：打开文档编辑器和参考资料",
                "steps": [
                    {
                        "tool": "app_control",
                        "params": {"action": "open", "app_name": "notepad"},
                        "description": "打开记事本"
                    },
                    {
                        "tool": "browser_control",
                        "params": {"action": "search", "query": "创作灵感"},
                        "description": "搜索创作灵感"
                    },
                    {
                        "tool": "media_control",
                        "params": {"action": "play_music", "music_query": "纯音乐"},
                        "description": "播放纯音乐"
                    }
                ]
            },
            "study_mode": {
                "name": "学习模式",
                "description": "准备学习：打开浏览器和笔记工具",
                "steps": [
                    {
                        "tool": "app_control",
                        "params": {"action": "open", "app_name": "notepad"},
                        "description": "打开笔记本"
                    },
                    {
                        "tool": "browser_control",
                        "params": {"action": "open", "url": "https://www.baidu.com"},
                        "description": "打开百度"
                    },
                    {
                        "tool": "media_control",
                        "params": {"action": "volume", "level": 20},
                        "description": "降低音量"
                    }
                ]
            },
            "relax_mode": {
                "name": "放松模式",
                "description": "休息放松：播放音乐并打开娱乐网站",
                "steps": [
                    {
                        "tool": "media_control",
                        "params": {"action": "play_music", "music_query": "放松音乐"},
                        "description": "播放放松音乐"
                    },
                    {
                        "tool": "media_control",
                        "params": {"action": "volume", "level": 40},
                        "description": "设置音量为40%"
                    },
                    {
                        "tool": "browser_control",
                        "params": {"action": "open", "url": "https://www.bilibili.com"},
                        "description": "打开B站"
                    }
                ]
            }
        }
    
    async def execute(self, scene_name: str, **kwargs) -> ToolResult:
        """执行场景"""
        try:
            # 获取场景配置
            scene = self.scenes.get(scene_name)
            if not scene:
                return ToolResult(
                    success=False,
                    message=f"未找到场景: {scene_name}",
                    error="Scene not found"
                )
            
            logger.info(f"🎬 开始执行场景: {scene['name']}")
            
            # 执行场景步骤
            results = []
            success_count = 0
            fail_count = 0
            
            for step in scene["steps"]:
                tool_name = step["tool"]
                tool_params = step["params"]
                description = step["description"]
                
                logger.info(f"  ▶ {description}")
                
                # 获取工具
                tool = tool_registry.get_tool(tool_name)
                if not tool:
                    logger.warning(f"    ⚠️ 工具不存在: {tool_name}")
                    results.append({
                        "step": description,
                        "success": False,
                        "error": "Tool not found"
                    })
                    fail_count += 1
                    continue
                
                # 执行工具
                result = await tool.safe_execute(**tool_params)
                results.append({
                    "step": description,
                    "success": result.success,
                    "message": result.message,
                    "error": result.error
                })
                
                if result.success:
                    logger.info(f"    ✅ {result.message}")
                    success_count += 1
                else:
                    logger.warning(f"    ❌ {result.message}")
                    fail_count += 1
            
            # 生成总结
            total = len(scene["steps"])
            summary = f"场景'{scene['name']}'执行完成：成功{success_count}/{total}，失败{fail_count}/{total}"
            
            return ToolResult(
                success=success_count > 0,
                message=summary,
                data={
                    "scene_name": scene["name"],
                    "total_steps": total,
                    "success_count": success_count,
                    "fail_count": fail_count,
                    "results": results
                }
            )
        
        except Exception as e:
            logger.error(f"场景执行失败: {e}")
            return ToolResult(
                success=False,
                message=f"场景执行失败: {e}",
                error=str(e)
            )
    
    def get_available_scenes(self) -> List[Dict]:
        """获取可用场景列表"""
        return [
            {
                "id": scene_id,
                "name": scene["name"],
                "description": scene["description"]
            }
            for scene_id, scene in self.scenes.items()
        ]


# 创建实例并注册
scene_manager_tool = SceneManagerTool()
tool_registry.register(scene_manager_tool)

