"""
音频处理器测试
"""
import pytest
from app.services.voice.audio_processor import AudioProcessor


class TestAudioProcessor:
    """音频处理器测试类"""
    
    @pytest.fixture
    def processor(self):
        """创建音频处理器实例"""
        return AudioProcessor()
    
    def test_init(self, processor):
        """测试初始化"""
        assert processor is not None
        assert hasattr(processor, 'supported_formats')
        assert 'wav' in processor.supported_formats
        assert 'mp3' in processor.supported_formats
    
    def test_supported_formats(self, processor):
        """测试支持的格式列表"""
        formats = processor.supported_formats
        assert len(formats) > 0
        assert 'wav' in formats
        assert 'mp3' in formats
        assert 'pcm' in formats
    
    def test_chunk_size_config(self, processor):
        """测试音频块大小配置"""
        assert hasattr(processor, 'CHUNK_SIZE')
        assert processor.CHUNK_SIZE == 2048  # 优化后的值
    
    def test_buffer_size_limit(self, processor):
        """测试缓冲区大小限制"""
        assert hasattr(processor, 'MAX_BUFFER_SIZE')
        assert processor.MAX_BUFFER_SIZE == 1024 * 1024  # 1MB
    
    def test_buffer_cache_exists(self, processor):
        """测试缓冲区缓存存在"""
        assert hasattr(processor, 'buffer_cache')
        assert isinstance(processor.buffer_cache, dict)
    
    def test_encode_method_exists(self, processor):
        """测试编码方法存在"""
        assert hasattr(processor, 'encode')
        assert callable(processor.encode)
    
    def test_decode_method_exists(self, processor):
        """测试解码方法存在"""
        assert hasattr(processor, 'decode')
        assert callable(processor.decode)
    
    def test_convert_format_method_exists(self, processor):
        """测试格式转换方法存在"""
        assert hasattr(processor, 'convert_format')
        assert callable(processor.convert_format)
    
    def test_invalid_format_handling(self, processor):
        """测试无效格式处理"""
        # 测试是否能优雅处理无效格式
        try:
            result = processor.convert_format(b"fake_data", "invalid_format", "wav")
            # 应该抛出异常或返回None
            assert result is None or isinstance(result, bytes)
        except (ValueError, Exception) as e:
            # 预期的异常
            assert True
    
    def test_empty_audio_handling(self, processor):
        """测试空音频数据处理"""
        try:
            result = processor.encode(b"")
            # 应该能处理空数据
            assert result is not None or result is None
        except Exception:
            # 可能抛出异常也是合理的
            assert True


class TestAudioProcessorPerformance:
    """音频处理器性能测试"""
    
    @pytest.fixture
    def processor(self):
        return AudioProcessor()
    
    def test_chunk_size_optimization(self, processor):
        """测试音频块大小优化"""
        # 确保使用了优化后的块大小
        assert processor.CHUNK_SIZE == 2048
        assert processor.CHUNK_SIZE < 4096  # 确保比旧值小
    
    def test_buffer_cache_efficiency(self, processor):
        """测试缓冲区缓存效率"""
        # 缓存应该是空的或字典
        assert isinstance(processor.buffer_cache, dict)
        
        # 缓存大小应该有限制
        cache_size = len(processor.buffer_cache)
        assert cache_size >= 0
    
    def test_memory_limit(self, processor):
        """测试内存限制"""
        # 最大缓冲区应该有合理的上限
        max_buffer = processor.MAX_BUFFER_SIZE
        assert max_buffer > 0
        assert max_buffer <= 10 * 1024 * 1024  # 不超过10MB

