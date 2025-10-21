"""
任务相关API - 集成工具执行
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from app.tools.base_tool import tool_registry
from app.utils.logger import logger

router = APIRouter()


class ExecuteTaskRequest(BaseModel):
    """执行任务请求"""
    tool_name: str
    params: Dict[str, Any]


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    status: str
    result: Optional[Dict] = None
    error: Optional[str] = None


@router.post("/execute")
async def execute_task(request: ExecuteTaskRequest):
    """
    执行工具任务
    
    - 接收工具名和参数
    - 执行工具
    - 返回结果
    """
    try:
        tool_name = request.tool_name
        params = request.params
        
        logger.info(f"📋 收到任务: {tool_name} with {params}")
        
        # 获取工具
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(
                status_code=404,
                detail=f"工具不存在: {tool_name}"
            )
        
        # 执行工具
        result = await tool.safe_execute(**params)
        
        return {
            "task_id": str(uuid.uuid4()),
            "status": "completed" if result.success else "failed",
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "error": result.error
        }
    
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    获取任务状态
    """
    # TODO: 实现任务状态查询
    return TaskStatus(
        task_id=task_id,
        status="completed",
        result={}
    )


@router.post("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """
    取消任务
    """
    # TODO: 实现任务取消
    return {
        "success": True,
        "message": f"任务 {task_id} 已取消"
    }


@router.get("/tools")
async def get_available_tools():
    """
    获取所有可用工具
    """
    tools = tool_registry.get_all_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "schema": tool.get_schema()
            }
            for tool in tools.values()
        ]
    }


@router.get("/tools/{tool_name}/schema")
async def get_tool_schema(tool_name: str):
    """
    获取工具schema
    """
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    return tool.get_schema()
