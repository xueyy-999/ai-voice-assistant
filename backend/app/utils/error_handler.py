"""
统一错误处理工具
"""
from typing import Dict, Any
from fastapi import HTTPException
from app.utils.logger import logger


class ErrorCode:
    """错误码定义"""
    # 通用错误 1xxx
    UNKNOWN_ERROR = 1000
    INVALID_PARAMETER = 1001
    UNAUTHORIZED = 1002
    FORBIDDEN = 1003
    NOT_FOUND = 1004
    
    # 语音服务错误 2xxx
    VOICE_RECOGNITION_FAILED = 2001
    VOICE_SYNTHESIS_FAILED = 2002
    AUDIO_FORMAT_INVALID = 2003
    AUDIO_TOO_LONG = 2004
    AUDIO_TOO_SHORT = 2005
    
    # AI服务错误 3xxx
    AI_SERVICE_ERROR = 3001
    AI_API_KEY_INVALID = 3002
    AI_RATE_LIMIT = 3003
    AI_TIMEOUT = 3004
    
    # 工具执行错误 4xxx
    TOOL_EXECUTION_FAILED = 4001
    APP_NOT_FOUND = 4002
    FILE_NOT_FOUND = 4003
    PERMISSION_DENIED = 4004
    
    # 会话错误 5xxx
    SESSION_NOT_FOUND = 5001
    SESSION_EXPIRED = 5002


class ErrorMessage:
    """用户友好的错误提示"""
    
    ERROR_MESSAGES: Dict[int, str] = {
        # 通用错误
        ErrorCode.UNKNOWN_ERROR: "系统错误，请稍后重试",
        ErrorCode.INVALID_PARAMETER: "请求参数不正确",
        ErrorCode.UNAUTHORIZED: "未授权访问",
        ErrorCode.FORBIDDEN: "没有权限执行此操作",
        ErrorCode.NOT_FOUND: "请求的资源不存在",
        
        # 语音服务
        ErrorCode.VOICE_RECOGNITION_FAILED: "语音识别失败，请重新录音",
        ErrorCode.VOICE_SYNTHESIS_FAILED: "语音合成失败，请稍后重试",
        ErrorCode.AUDIO_FORMAT_INVALID: "音频格式不支持，请使用WAV或MP3格式",
        ErrorCode.AUDIO_TOO_LONG: "音频时长超过限制（最长60秒）",
        ErrorCode.AUDIO_TOO_SHORT: "音频太短，请说完整的指令",
        
        # AI服务
        ErrorCode.AI_SERVICE_ERROR: "AI服务暂时不可用，请稍后重试",
        ErrorCode.AI_API_KEY_INVALID: "AI服务配置错误，请联系管理员",
        ErrorCode.AI_RATE_LIMIT: "请求过于频繁，请稍后再试",
        ErrorCode.AI_TIMEOUT: "AI响应超时，请重试",
        
        # 工具执行
        ErrorCode.TOOL_EXECUTION_FAILED: "操作执行失败",
        ErrorCode.APP_NOT_FOUND: "未找到指定的应用程序",
        ErrorCode.FILE_NOT_FOUND: "文件不存在",
        ErrorCode.PERMISSION_DENIED: "权限不足，请以管理员身份运行",
        
        # 会话
        ErrorCode.SESSION_NOT_FOUND: "会话不存在或已过期",
        ErrorCode.SESSION_EXPIRED: "会话已过期，请刷新页面",
    }
    
    @classmethod
    def get_message(cls, error_code: int, default: str = "未知错误") -> str:
        """获取错误提示信息"""
        return cls.ERROR_MESSAGES.get(error_code, default)


class AppError(Exception):
    """应用异常基类"""
    
    def __init__(
        self, 
        error_code: int,
        message: str = None,
        details: Any = None,
        http_status: int = 500
    ):
        self.error_code = error_code
        self.message = message or ErrorMessage.get_message(error_code)
        self.details = details
        self.http_status = http_status
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "error_code": self.error_code,
            "message": self.message
        }
        if self.details:
            result["details"] = self.details
        return result


class VoiceError(AppError):
    """语音服务异常"""
    
    def __init__(self, error_code: int, message: str = None, details: Any = None):
        super().__init__(error_code, message, details, http_status=400)


class AIError(AppError):
    """AI服务异常"""
    
    def __init__(self, error_code: int, message: str = None, details: Any = None):
        super().__init__(error_code, message, details, http_status=503)


class ToolError(AppError):
    """工具执行异常"""
    
    def __init__(self, error_code: int, message: str = None, details: Any = None):
        super().__init__(error_code, message, details, http_status=500)


def handle_error(error: Exception) -> HTTPException:
    """
    统一错误处理函数
    
    Args:
        error: 异常对象
    
    Returns:
        HTTPException: FastAPI异常对象
    """
    # 如果是应用自定义异常
    if isinstance(error, AppError):
        logger.error(f"应用错误 [{error.error_code}]: {error.message}", 
                    extra={"details": error.details})
        return HTTPException(
            status_code=error.http_status,
            detail=error.to_dict()
        )
    
    # 如果已经是HTTPException
    if isinstance(error, HTTPException):
        return error
    
    # 其他未知异常
    logger.error(f"未知错误: {str(error)}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail={
            "error_code": ErrorCode.UNKNOWN_ERROR,
            "message": ErrorMessage.get_message(ErrorCode.UNKNOWN_ERROR)
        }
    )


def validate_audio_duration(duration: float, max_duration: float = 60.0) -> None:
    """
    验证音频时长
    
    Args:
        duration: 音频时长（秒）
        max_duration: 最大允许时长
    
    Raises:
        VoiceError: 时长超限
    """
    if duration > max_duration:
        raise VoiceError(
            ErrorCode.AUDIO_TOO_LONG,
            details=f"音频时长{duration:.1f}秒，最长{max_duration:.1f}秒"
        )
    
    if duration < 0.5:
        raise VoiceError(
            ErrorCode.AUDIO_TOO_SHORT,
            details="音频时长不足0.5秒"
        )


def validate_text_length(text: str, max_length: int = 500) -> None:
    """
    验证文本长度
    
    Args:
        text: 文本内容
        max_length: 最大长度
    
    Raises:
        AppError: 长度超限
    """
    if len(text) > max_length:
        raise AppError(
            ErrorCode.INVALID_PARAMETER,
            f"文本长度超过限制（最长{max_length}字符）",
            http_status=400
        )
    
    if not text.strip():
        raise AppError(
            ErrorCode.INVALID_PARAMETER,
            "文本内容不能为空",
            http_status=400
        )

