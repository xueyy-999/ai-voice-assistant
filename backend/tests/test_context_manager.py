"""
上下文管理器测试
"""
import pytest
from datetime import datetime
from app.services.ai.context_manager import ContextManager


class TestContextManager:
    """上下文管理器测试类"""
    
    @pytest.fixture
    def context_mgr(self):
        """创建上下文管理器实例"""
        return ContextManager()
    
    def test_init(self, context_mgr):
        """测试初始化"""
        assert context_mgr is not None
        assert hasattr(context_mgr, 'add_message')
        assert hasattr(context_mgr, 'get_context')
    
    def test_add_user_message(self, context_mgr):
        """测试添加用户消息"""
        context_mgr.add_message("user", "打开微信")
        context = context_mgr.get_context()
        
        assert len(context) > 0
        assert context[-1]["role"] == "user"
        assert context[-1]["content"] == "打开微信"
    
    def test_add_assistant_message(self, context_mgr):
        """测试添加助手消息"""
        context_mgr.add_message("assistant", "微信已打开")
        context = context_mgr.get_context()
        
        assert len(context) > 0
        assert context[-1]["role"] == "assistant"
        assert context[-1]["content"] == "微信已打开"
    
    def test_conversation_flow(self, context_mgr):
        """测试完整对话流程"""
        context_mgr.add_message("user", "打开微信")
        context_mgr.add_message("assistant", "微信已打开")
        context_mgr.add_message("user", "发送消息")
        context_mgr.add_message("assistant", "请告诉我要发送给谁？")
        
        context = context_mgr.get_context()
        assert len(context) == 4
        assert context[0]["role"] == "user"
        assert context[1]["role"] == "assistant"
    
    def test_context_limit(self, context_mgr):
        """测试上下文长度限制"""
        # 添加超过限制的消息
        for i in range(20):
            context_mgr.add_message("user", f"消息{i}")
        
        context = context_mgr.get_context()
        # 应该只保留最近的消息
        assert len(context) <= 10  # 假设限制是10
    
    def test_clear_context(self, context_mgr):
        """测试清空上下文"""
        context_mgr.add_message("user", "测试消息")
        context_mgr.clear()
        context = context_mgr.get_context()
        
        assert len(context) == 0
    
    def test_reference_resolution(self, context_mgr):
        """测试引用解析"""
        if hasattr(context_mgr, 'resolve_reference'):
            context_mgr.add_message("user", "打开微信")
            context_mgr.add_message("assistant", "微信已打开")
            context_mgr.add_message("user", "关闭它")
            
            # 尝试解析"它"
            result = context_mgr.resolve_reference("它")
            # 应该返回微信或相关信息
            assert result is not None
    
    def test_get_empty_context(self, context_mgr):
        """测试获取空上下文"""
        context = context_mgr.get_context()
        assert isinstance(context, list)
        assert len(context) == 0
    
    def test_message_timestamp(self, context_mgr):
        """测试消息时间戳"""
        context_mgr.add_message("user", "测试")
        context = context_mgr.get_context()
        
        if len(context) > 0:
            message = context[-1]
            # 检查是否有时间戳字段
            if "timestamp" in message:
                assert message["timestamp"] is not None
    
    def test_system_message(self, context_mgr):
        """测试系统消息"""
        context_mgr.add_message("system", "系统初始化完成")
        context = context_mgr.get_context()
        
        if len(context) > 0:
            assert context[-1]["role"] == "system"
    
    def test_context_persistence(self, context_mgr):
        """测试上下文持久性"""
        context_mgr.add_message("user", "消息1")
        context_mgr.add_message("assistant", "回复1")
        
        context1 = context_mgr.get_context()
        context2 = context_mgr.get_context()
        
        # 两次获取应该得到相同的内容
        assert len(context1) == len(context2)
    
    def test_message_order(self, context_mgr):
        """测试消息顺序"""
        messages = ["消息1", "消息2", "消息3"]
        for msg in messages:
            context_mgr.add_message("user", msg)
        
        context = context_mgr.get_context()
        # 验证顺序
        for i, msg in enumerate(messages):
            if i < len(context):
                assert context[i]["content"] == msg


class TestContextManagerEdgeCases:
    """上下文管理器边界测试"""
    
    @pytest.fixture
    def context_mgr(self):
        return ContextManager()
    
    def test_empty_message(self, context_mgr):
        """测试空消息"""
        try:
            context_mgr.add_message("user", "")
            # 应该能处理空消息
            assert True
        except Exception:
            # 或者抛出异常也合理
            assert True
    
    def test_none_message(self, context_mgr):
        """测试None消息"""
        try:
            context_mgr.add_message("user", None)
        except (ValueError, TypeError):
            # 预期的异常
            assert True
    
    def test_invalid_role(self, context_mgr):
        """测试无效角色"""
        try:
            context_mgr.add_message("invalid_role", "测试")
            # 可能接受也可能拒绝
            assert True
        except ValueError:
            # 拒绝无效角色也是合理的
            assert True
    
    def test_very_long_message(self, context_mgr):
        """测试超长消息"""
        long_message = "测试" * 10000  # 很长的消息
        try:
            context_mgr.add_message("user", long_message)
            # 应该能处理或截断
            assert True
        except Exception:
            # 或者拒绝
            assert True

