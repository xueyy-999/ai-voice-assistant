"""
对话相关API - 集成Agent服务
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import time
from app.utils.logger import logger
from app.services.ai.agent_service import agent_service
from app.services.ai.context_manager import context_manager

router = APIRouter()


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    message: str
    session_id: Optional[str] = None


@router.post("/send")
async def send_message(request: SendMessageRequest):
    """
    发送对话消息 - 使用Agent执行
    
    - 接收用户消息
    - 通过Agent智能执行
    - 返回AI回复和执行结果
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        user_message = request.message
        
        logger.info(f"📨 收到消息: {user_message}")
        
        # 获取会话上下文
        context = await context_manager.get_context(session_id)
        
        # 如果是新会话，创建
        if not context.get("history"):
            await context_manager.create_session(session_id)
        
        # 保存用户消息
        await context_manager.add_message(session_id, "user", user_message)
        
        # 解析指代
        resolved_message = context_manager.resolve_reference(
            user_message,
            context
        )
        
        # 使用Agent执行
        chat_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in context.get("history", [])[-5:]  # 最近5条
        ]
        
        result = await agent_service.execute(resolved_message, chat_history)
        
        reply = result["output"]
        steps = result["intermediate_steps"]
        
        logger.info(f"💬 AI回复: {reply}")
        
        # 保存AI回复
        await context_manager.add_message(session_id, "assistant", reply)
        
        # 更新上下文（保存最后的实体）
        if steps:
            last_tool_input = steps[-1].get("tool_input", {})
            if "app_name" in last_tool_input:
                await context_manager.update_context(session_id, {
                    "last_entity": last_tool_input["app_name"]
                })
        
        return {
            "session_id": session_id,
            "reply": reply,
            "steps": steps,
            "success": result["success"]
        }
    
    except Exception as e:
        logger.error(f"对话处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(session_id: str, limit: int = 50):
    """
    获取对话历史
    """
    try:
        history = await context_manager.get_chat_history(session_id, limit)
        return {"messages": history}
    except Exception as e:
        logger.error(f"获取历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ConnectionManager:
    """WebSocket连接管理器 - 性能优化版"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self.message_queue = {}  # 消息队列，支持优先级处理
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket已连接，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"👋 WebSocket已断开，当前连接数: {len(self.active_connections)}")
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message, ensure_ascii=False))


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket连接 - 支持实时Agent执行
    """
    await manager.connect(websocket)
    session_id = str(uuid.uuid4())
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            msg_data = message.get("data", {})
            
            logger.info(f"📨 WS收到: {msg_type}")
            
            # 处理不同类型的消息
            if msg_type == "ping":
                # 心跳
                await manager.send_message({
                    "type": "pong",
                    "timestamp": int(time.time() * 1000)
                }, websocket)
            
            elif msg_type in ("chat", "text", "message"):
                # 对话消息
                user_message = msg_data.get("text") or msg_data.get("content") or msg_data if isinstance(msg_data, str) else ""
                
                # 推送"思考中"状态
                await manager.send_message({
                    "type": "thinking",
                    "data": {"status": "processing"}
                }, websocket)
                
                # 获取上下文
                context = await context_manager.get_context(session_id)
                if not context.get("history"):
                    await context_manager.create_session(session_id)
                
                # 保存用户消息
                await context_manager.add_message(session_id, "user", user_message)
                
                # Agent执行
                chat_history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in context.get("history", [])[-5:]
                ]
                
                result = await agent_service.execute(user_message, chat_history)
                
                # 保存AI回复
                await context_manager.add_message(session_id, "assistant", result["output"])
                
                # 推送执行步骤
                for i, step in enumerate(result["intermediate_steps"]):
                    await manager.send_message({
                        "type": "step_update",
                        "data": {
                            "step_index": i,
                            "tool": step["tool"],
                            "status": "completed",
                            "result": step["result"]
                        }
                    }, websocket)
                
                # 发送最终回复
                await manager.send_message({
                    "type": "chat_response",
                    "data": {
                        "text": result["output"],
                        "steps": result["intermediate_steps"],
                        "success": result["success"]
                    },
                    "timestamp": int(time.time() * 1000)
                }, websocket)
            
            else:
                logger.warning(f"未知消息类型: {msg_type}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket错误: {e}")
        manager.disconnect(websocket)
