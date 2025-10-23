"""
性能监控中间件
FastAPI中间件，自动记录每个请求的性能指标
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger
from app.utils.performance_monitor import monitor


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求并记录性能"""
        # 记录开始时间
        start_time = time.time()
        
        # 获取端点信息
        endpoint = f"{request.method} {request.url.path}"
        
        # 记录请求
        monitor.record_request(endpoint)
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 记录延迟
            duration = time.time() - start_time
            monitor.record_latency(endpoint, duration)
            
            # 添加性能头
            response.headers["X-Process-Time"] = f"{duration:.3f}s"
            
            # 记录日志
            logger.info(
                f"📊 {endpoint} | "
                f"Status: {response.status_code} | "
                f"Time: {duration:.3f}s"
            )
            
            # 慢请求告警
            if duration > 2.0:
                logger.warning(f"⏱️ 慢请求告警: {endpoint} 耗时 {duration:.2f}s")
            
            return response
            
        except Exception as e:
            # 记录错误
            duration = time.time() - start_time
            monitor.record_error(endpoint, type(e).__name__)
            
            logger.error(
                f"❌ {endpoint} | "
                f"Error: {type(e).__name__} | "
                f"Time: {duration:.3f}s"
            )
            
            raise

