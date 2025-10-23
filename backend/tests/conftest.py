"""
Pytest配置文件
定义全局fixtures和配置
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_audio_data():
    """提供测试用的音频数据"""
    # 生成简单的PCM数据
    return b'\x00\x01' * 1000  # 简单的测试数据


@pytest.fixture(scope="session")
def test_config():
    """提供测试配置"""
    return {
        "test_mode": True,
        "mock_services": True,
        "timeout": 5,
    }


@pytest.fixture
def mock_llm_response():
    """模拟LLM响应"""
    return {
        "text": "这是一个测试回复",
        "confidence": 0.95,
        "tokens": 100,
    }


@pytest.fixture
def sample_messages():
    """提供示例消息列表"""
    return [
        {"role": "user", "content": "打开微信"},
        {"role": "assistant", "content": "微信已打开"},
        {"role": "user", "content": "发送消息"},
    ]


@pytest.fixture(autouse=True)
def reset_environment():
    """每个测试前重置环境"""
    yield
    # 测试后清理
    pass


# 配置pytest
def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line(
        "markers", "slow: 标记慢速测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记集成测试"
    )
    config.addinivalue_line(
        "markers", "unit: 标记单元测试"
    )

