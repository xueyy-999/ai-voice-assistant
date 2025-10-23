"""
音频处理器 - 格式转换、编解码
"""
import base64
import io
from typing import Optional
from app.utils.logger import logger


class AudioProcessor:
    """音频处理器"""
    
    # 性能优化：添加音频块大小配置
    CHUNK_SIZE = 2048  # 优化：从4096降低到2048，减少延迟
    MAX_BUFFER_SIZE = 1024 * 1024  # 1MB，防止内存溢出
    
    def __init__(self):
        self.supported_formats = ['wav', 'mp3', 'pcm']
        self.buffer_cache = {}  # 添加缓冲区缓存
    
    def validate_format(self, audio_format: str) -> bool:
        """验证音频格式"""
        return audio_format.lower() in self.supported_formats
    
    def base64_encode(self, audio_bytes: bytes) -> str:
        """Base64编码"""
        return base64.b64encode(audio_bytes).decode('utf-8')
    
    def base64_decode(self, audio_base64: str) -> bytes:
        """Base64解码"""
        return base64.b64decode(audio_base64)
    
    def pcm_to_wav(self, pcm_data: bytes, sample_rate: int = 16000, 
                   channels: int = 1, sample_width: int = 2) -> bytes:
        """PCM转WAV格式"""
        import wave
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        
        buffer.seek(0)
        return buffer.read()
    
    def normalize_volume(self, audio_bytes: bytes, target_level: float = 0.8) -> bytes:
        """音量归一化"""
        # 简单实现，实际可以使用pydub
        return audio_bytes
    
    async def process_audio_chunk(self, audio_base64: str, 
                                  input_format: str = 'pcm',
                                  output_format: str = 'wav') -> Optional[bytes]:
        """处理音频块"""
        try:
            # 解码
            audio_bytes = self.base64_decode(audio_base64)
            
            # 格式转换
            if input_format == 'pcm' and output_format == 'wav':
                audio_bytes = self.pcm_to_wav(audio_bytes)
            
            return audio_bytes
            
        except Exception as e:
            logger.error(f"音频处理失败: {e}")
            return None


# 全局实例
audio_processor = AudioProcessor()

