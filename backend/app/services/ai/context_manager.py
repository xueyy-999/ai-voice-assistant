"""
上下文管理器 - 会话历史和上下文
"""
from typing import List, Dict, Optional
import json
from datetime import datetime
from app.database.sqlite_db import db
from app.utils.logger import logger


class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.max_history = 10  # 最多保留10轮对话
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话"""
        try:
            row = await db.fetchone(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,)
            )
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return None
    
    async def create_session(self, session_id: str) -> bool:
        """创建会话"""
        try:
            await db.execute(
                "INSERT INTO sessions (id, status, context) VALUES (?, ?, ?)",
                (session_id, "active", "{}")
            )
            logger.info(f"✅ 创建会话: {session_id}")
            return True
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            return False
    
    async def add_message(self, session_id: str, role: str, content: str,
                         message_type: str = "text") -> bool:
        """添加消息"""
        try:
            import uuid
            message_id = str(uuid.uuid4())
            
            await db.execute(
                """INSERT INTO messages (id, session_id, role, content, type)
                   VALUES (?, ?, ?, ?, ?)""",
                (message_id, session_id, role, content, message_type)
            )
            
            logger.info(f"💬 添加消息: {role} - {content[:50]}...")
            return True
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            return False
    
    async def get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """获取对话历史"""
        try:
            rows = await db.fetchall(
                """SELECT role, content, timestamp FROM messages
                   WHERE session_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (session_id, limit)
            )
            
            # 反转顺序（从旧到新）
            messages = [dict(row) for row in reversed(rows)]
            
            return messages
        except Exception as e:
            logger.error(f"获取历史失败: {e}")
            return []
    
    async def get_context(self, session_id: str) -> Dict:
        """获取会话上下文"""
        try:
            # 获取最近的对话
            history = await self.get_chat_history(session_id, self.max_history)
            
            # 获取会话数据
            session = await self.get_session(session_id)
            context_data = {}
            if session and session.get("context"):
                try:
                    context_data = json.loads(session["context"])
                except:
                    pass
            
            return {
                "session_id": session_id,
                "history": history,
                "context": context_data
            }
        except Exception as e:
            logger.error(f"获取上下文失败: {e}")
            return {"session_id": session_id, "history": [], "context": {}}
    
    async def update_context(self, session_id: str, context_data: Dict) -> bool:
        """更新会话上下文"""
        try:
            context_json = json.dumps(context_data, ensure_ascii=False)
            
            await db.execute(
                "UPDATE sessions SET context = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (context_json, session_id)
            )
            
            logger.info(f"📝 更新上下文: {session_id}")
            return True
        except Exception as e:
            logger.error(f"更新上下文失败: {e}")
            return False
    
    def resolve_reference(self, text: str, context: Dict) -> str:
        """解析指代（"它"、"那个"等）"""
        # 简单实现：从上下文中查找最后提到的实体
        last_entity = context.get("context", {}).get("last_entity")
        
        if last_entity:
            text = text.replace("它", last_entity)
            text = text.replace("那个", last_entity)
        
        return text


# 全局实例
context_manager = ContextManager()

