"""
意图解析器测试
"""
import pytest
from app.services.ai.intent_parser import IntentParser, Intent


class TestIntentParser:
    """意图解析器测试类"""
    
    @pytest.fixture
    def parser(self):
        """创建解析器实例"""
        return IntentParser()
    
    def test_app_control_open(self, parser):
        """测试应用打开意图识别"""
        result = parser._rule_based_parse("打开微信")
        assert result.type == "app_control"
        assert result.action == "open"
        assert "微信" in result.entities.get("app", "")
        assert result.confidence > 0.8
    
    def test_app_control_close(self, parser):
        """测试应用关闭意图识别"""
        result = parser._rule_based_parse("关闭浏览器")
        assert result.type == "app_control"
        assert result.action == "close"
        assert "浏览器" in result.entities.get("app", "")
    
    def test_file_operation_create(self, parser):
        """测试文件创建意图识别"""
        result = parser._rule_based_parse("创建一个文件叫test.txt")
        assert result.type == "file_operation"
        assert result.action == "create"
        assert "test.txt" in result.raw_text
    
    def test_file_operation_delete(self, parser):
        """测试文件删除意图识别"""
        result = parser._rule_based_parse("删除这个文件")
        assert result.type == "file_operation"
        assert result.action == "delete"
    
    def test_browser_control_search(self, parser):
        """测试浏览器搜索意图识别"""
        result = parser._rule_based_parse("搜索Python教程")
        assert result.type == "browser_control"
        assert result.action == "search"
        assert "Python教程" in result.entities.get("query", "")
    
    def test_browser_control_open(self, parser):
        """测试浏览器打开网页意图识别"""
        result = parser._rule_based_parse("打开百度网页")
        assert result.type == "browser_control"
        assert result.action == "open"
    
    def test_media_control_play(self, parser):
        """测试媒体播放意图识别"""
        result = parser._rule_based_parse("播放音乐")
        assert result.type == "media_control"
        assert result.action == "play"
    
    def test_media_control_pause(self, parser):
        """测试媒体暂停意图识别"""
        result = parser._rule_based_parse("暂停播放")
        assert result.type == "media_control"
        assert result.action == "pause"
    
    def test_media_control_volume(self, parser):
        """测试音量控制意图识别"""
        result = parser._rule_based_parse("音量加大")
        assert result.type == "media_control"
        assert "volume" in result.action or "音量" in result.raw_text
    
    def test_scene_manager_work(self, parser):
        """测试场景切换 - 工作模式"""
        result = parser._rule_based_parse("进入工作模式")
        assert result.type == "scene_manager"
        assert "工作" in result.raw_text or "work" in result.action
    
    def test_scene_manager_meeting(self, parser):
        """测试场景切换 - 会议模式"""
        result = parser._rule_based_parse("准备开会")
        assert result.type == "scene_manager"
    
    def test_text_processing_copy(self, parser):
        """测试文本处理 - 复制"""
        result = parser._rule_based_parse("复制这段文字")
        assert result.type == "text_processing"
        assert result.action == "copy"
    
    def test_text_processing_paste(self, parser):
        """测试文本处理 - 粘贴"""
        result = parser._rule_based_parse("粘贴内容")
        assert result.type == "text_processing"
        assert result.action == "paste"
    
    def test_unknown_intent(self, parser):
        """测试未知意图"""
        result = parser._rule_based_parse("这是一段随机文字xyz123")
        # 应该返回chat或unknown
        assert result.type in ["chat", "unknown"]
    
    def test_confidence_score(self, parser):
        """测试置信度评分"""
        # 明确的命令应该有高置信度
        result1 = parser._rule_based_parse("打开微信")
        assert result1.confidence > 0.8
        
        # 模糊的命令置信度较低
        result2 = parser._rule_based_parse("微信")
        assert result2.confidence < 1.0
    
    def test_entity_extraction(self, parser):
        """测试实体提取"""
        result = parser._rule_based_parse("打开微信并发送消息")
        assert result.entities is not None
        assert isinstance(result.entities, dict)
    
    @pytest.mark.asyncio
    async def test_async_parse(self, parser):
        """测试异步解析接口"""
        result = await parser.parse("打开记事本")
        assert result is not None
        assert result.type == "app_control"
        assert result.action == "open"
    
    def test_special_characters(self, parser):
        """测试特殊字符处理"""
        result = parser._rule_based_parse("打开《我的文档》")
        assert result.type == "file_operation" or result.type == "app_control"
    
    def test_english_commands(self, parser):
        """测试英文命令"""
        result = parser._rule_based_parse("open chrome")
        # 应该能识别或返回unknown
        assert result is not None
    
    def test_mixed_language(self, parser):
        """测试中英混合"""
        result = parser._rule_based_parse("打开Chrome浏览器")
        assert result.type == "app_control"
        assert result.action == "open"

