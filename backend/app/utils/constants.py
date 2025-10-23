"""
常量定义模块
统一管理项目中使用的常量
"""

# ==================== 错误码定义 ====================

class ErrorCode:
    """统一错误码"""
    
    # 通用错误 (1000-1999)
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    INVALID_PARAMETER = 1001
    PERMISSION_DENIED = 1002
    RESOURCE_NOT_FOUND = 1003
    TIMEOUT = 1004
    
    # API相关 (2000-2999)
    API_UNAVAILABLE = 2000
    API_TIMEOUT = 2001
    API_RATE_LIMIT = 2002
    API_KEY_INVALID = 2003
    
    # 语音服务 (3000-3999)
    STT_FAILED = 3000
    STT_TIMEOUT = 3001
    STT_FORMAT_ERROR = 3002
    TTS_FAILED = 3100
    TTS_TIMEOUT = 3101
    AUDIO_FORMAT_ERROR = 3200
    AUDIO_PROCESS_ERROR = 3201
    
    # AI服务 (4000-4999)
    LLM_UNAVAILABLE = 4000
    LLM_TIMEOUT = 4001
    INTENT_PARSE_ERROR = 4100
    AGENT_EXECUTION_ERROR = 4200
    
    # 工具执行 (5000-5999)
    TOOL_NOT_FOUND = 5000
    TOOL_EXECUTION_ERROR = 5001
    APP_CONTROL_ERROR = 5100
    FILE_OPERATION_ERROR = 5200
    BROWSER_CONTROL_ERROR = 5300


# ==================== 系统配置常量 ====================

class SystemConfig:
    """系统配置常量"""
    
    # 音频配置
    AUDIO_CHUNK_SIZE = 2048
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    MAX_BUFFER_SIZE = 1024 * 1024  # 1MB
    
    # WebSocket配置
    WS_HEARTBEAT_INTERVAL = 30  # 秒
    WS_TIMEOUT = 300  # 5分钟
    WS_MAX_CONNECTIONS = 100
    
    # LLM配置
    LLM_MAX_TOKENS = 2000
    LLM_TEMPERATURE = 0.7
    LLM_TIMEOUT = 30  # 秒
    
    # 上下文配置
    CONTEXT_MAX_HISTORY = 10  # 保留最近10轮对话
    CONTEXT_MAX_AGE = 3600  # 1小时后过期
    
    # 性能配置
    MAX_CONCURRENT_REQUESTS = 50
    REQUEST_TIMEOUT = 60  # 秒
    CACHE_TTL = 3600  # 1小时


# ==================== 工具类型定义 ====================

class ToolType:
    """工具类型"""
    
    APP_CONTROL = "app_control"
    FILE_OPERATION = "file_operation"
    BROWSER_CONTROL = "browser_control"
    TEXT_PROCESSING = "text_processing"
    MEDIA_CONTROL = "media_control"
    SCENE_MANAGER = "scene_manager"
    SYSTEM_COMMAND = "system_command"


# ==================== 意图类型定义 ====================

class IntentType:
    """意图类型"""
    
    APP_CONTROL = "app_control"
    FILE_OPERATION = "file_operation"
    BROWSER_CONTROL = "browser_control"
    TEXT_PROCESSING = "text_processing"
    MEDIA_CONTROL = "media_control"
    SCENE_MANAGER = "scene_manager"
    CHAT = "chat"
    UNKNOWN = "unknown"


# ==================== 操作类型定义 ====================

class ActionType:
    """操作类型"""
    
    # 应用操作
    APP_OPEN = "open"
    APP_CLOSE = "close"
    APP_SWITCH = "switch"
    
    # 文件操作
    FILE_CREATE = "create"
    FILE_DELETE = "delete"
    FILE_RENAME = "rename"
    FILE_MOVE = "move"
    FILE_SEARCH = "search"
    
    # 浏览器操作
    BROWSER_OPEN = "open"
    BROWSER_SEARCH = "search"
    BROWSER_BOOKMARK = "bookmark"
    
    # 媒体操作
    MEDIA_PLAY = "play"
    MEDIA_PAUSE = "pause"
    MEDIA_STOP = "stop"
    MEDIA_VOLUME_UP = "volume_up"
    MEDIA_VOLUME_DOWN = "volume_down"


# ==================== 场景类型定义 ====================

class SceneType:
    """场景类型"""
    
    WORK = "work"           # 工作模式
    ENTERTAINMENT = "entertainment"  # 娱乐模式
    MEETING = "meeting"     # 会议模式
    FOCUS = "focus"         # 专注模式
    REST = "rest"           # 休息模式


# ==================== 日志级别 ====================

class LogLevel:
    """日志级别"""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ==================== 响应状态 ====================

class ResponseStatus:
    """响应状态"""
    
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    TIMEOUT = "timeout"


# ==================== 文件类型 ====================

class FileType:
    """文件类型"""
    
    # 音频格式
    AUDIO_WAV = "wav"
    AUDIO_MP3 = "mp3"
    AUDIO_PCM = "pcm"
    AUDIO_OGG = "ogg"
    
    # 文档格式
    DOC_TXT = "txt"
    DOC_PDF = "pdf"
    DOC_DOCX = "docx"
    DOC_MD = "md"


# ==================== 正则表达式模式 ====================

class RegexPattern:
    """常用正则表达式"""
    
    # 应用名称
    APP_NAME = r'[a-zA-Z0-9\u4e00-\u9fa5]+'
    
    # 文件路径
    FILE_PATH = r'[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*'
    
    # URL
    URL = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)'
    
    # 邮箱
    EMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


# ==================== 默认配置值 ====================

class DefaultValue:
    """默认值配置"""
    
    # 语音合成默认音色
    TTS_VOICE = "zh-CN-XiaoxiaoNeural"
    
    # 语音识别默认语言
    STT_LANGUAGE = "zh-CN"
    
    # 默认超时时间
    DEFAULT_TIMEOUT = 30
    
    # 默认重试次数
    DEFAULT_RETRY = 3
    
    # 默认置信度阈值
    CONFIDENCE_THRESHOLD = 0.7

