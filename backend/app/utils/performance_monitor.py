"""
性能监控模块
用于监控系统关键性能指标
"""
import time
import psutil
from typing import Dict, Optional
from functools import wraps
from app.utils.logger import logger


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            "requests": {},
            "latency": {},
            "errors": {},
            "resource": {}
        }
    
    def record_request(self, endpoint: str):
        """记录API请求"""
        if endpoint not in self.metrics["requests"]:
            self.metrics["requests"][endpoint] = 0
        self.metrics["requests"][endpoint] += 1
    
    def record_latency(self, endpoint: str, duration: float):
        """记录延迟"""
        if endpoint not in self.metrics["latency"]:
            self.metrics["latency"][endpoint] = []
        self.metrics["latency"][endpoint].append(duration)
        
        # 只保留最近100条记录
        if len(self.metrics["latency"][endpoint]) > 100:
            self.metrics["latency"][endpoint] = self.metrics["latency"][endpoint][-100:]
    
    def record_error(self, endpoint: str, error_type: str):
        """记录错误"""
        key = f"{endpoint}:{error_type}"
        if key not in self.metrics["errors"]:
            self.metrics["errors"][key] = 0
        self.metrics["errors"][key] += 1
    
    def get_system_metrics(self) -> Dict:
        """获取系统资源指标"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {}
    
    def get_latency_stats(self, endpoint: str) -> Optional[Dict]:
        """获取延迟统计"""
        if endpoint not in self.metrics["latency"]:
            return None
        
        latencies = self.metrics["latency"][endpoint]
        if not latencies:
            return None
        
        return {
            "count": len(latencies),
            "avg": sum(latencies) / len(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "p50": sorted(latencies)[len(latencies) // 2],
            "p95": sorted(latencies)[int(len(latencies) * 0.95)],
            "p99": sorted(latencies)[int(len(latencies) * 0.99)]
        }
    
    def get_summary(self) -> Dict:
        """获取监控摘要"""
        return {
            "total_requests": sum(self.metrics["requests"].values()),
            "total_errors": sum(self.metrics["errors"].values()),
            "endpoints": list(self.metrics["requests"].keys()),
            "system": self.get_system_metrics()
        }
    
    def reset(self):
        """重置所有指标"""
        self.metrics = {
            "requests": {},
            "latency": {},
            "errors": {},
            "resource": {}
        }
        logger.info("📊 性能监控指标已重置")


# 全局监控器实例
monitor = PerformanceMonitor()


def track_performance(endpoint: str = None):
    """
    性能追踪装饰器
    
    用法:
    @track_performance("api_endpoint_name")
    async def my_function():
        pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal endpoint
            if endpoint is None:
                endpoint = func.__name__
            
            # 记录请求
            monitor.record_request(endpoint)
            
            # 计时
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                # 记录错误
                monitor.record_error(endpoint, type(e).__name__)
                logger.error(f"⚠️ {endpoint} 执行失败: {e}")
                raise
            finally:
                # 记录延迟
                duration = time.time() - start_time
                monitor.record_latency(endpoint, duration)
                
                # 记录性能日志
                if duration > 1.0:  # 超过1秒记录警告
                    logger.warning(f"⏱️ {endpoint} 执行缓慢: {duration:.2f}s")
                else:
                    logger.debug(f"⏱️ {endpoint} 执行时间: {duration:.3f}s")
        
        return wrapper
    return decorator


def log_system_metrics():
    """记录系统指标"""
    metrics = monitor.get_system_metrics()
    
    logger.info(
        f"📊 系统指标: "
        f"CPU {metrics.get('cpu_percent', 0):.1f}% | "
        f"内存 {metrics.get('memory_percent', 0):.1f}% | "
        f"磁盘 {metrics.get('disk_percent', 0):.1f}%"
    )
    
    # 告警
    if metrics.get('cpu_percent', 0) > 80:
        logger.warning("⚠️ CPU使用率过高!")
    if metrics.get('memory_percent', 0) > 80:
        logger.warning("⚠️ 内存使用率过高!")
    if metrics.get('disk_percent', 0) > 90:
        logger.warning("⚠️ 磁盘空间不足!")

