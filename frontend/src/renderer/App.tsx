import React, { useEffect, useState } from 'react';
import { VoiceButton } from './components/VoiceButton';
import { ChatPanel } from './components/ChatPanel';
import { FlowVisualization } from './components/FlowVisualization';
import { useAppStore } from './store/useAppStore';
import { useChatStore } from './store/useChatStore';
import { wsClient } from './services/websocket';
import { api } from './services/api';

function App() {
  const { isConnected, setConnected, setSystemInfo } = useAppStore();
  const {
    currentSteps,
    setCurrentSteps,
    setCurrentStepIndex,
    clearSteps,
    addMessage,
    setThinking,
  } = useChatStore();
  const [activeTab, setActiveTab] = useState<'chat' | 'flow'>('chat');

  useEffect(() => {
    // 先注册WS事件，再发起连接，避免丢失ws_open事件
    wsClient.on('ws_open', () => setConnected(true));
    wsClient.on('ws_close', () => setConnected(false));
    wsClient.connect();

    // 并行初始化其它数据（健康检查/系统信息），不阻塞WS连接
    initApp();

    return () => {
      wsClient.disconnect();
    };
  }, []);

  const initApp = async () => {
    try {
      // 检查后端健康（超时保护）
      const health = await Promise.race([
        api.health(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('health_timeout')), 4000)),
      ]);
      console.log('✅ Backend health:', health);

      // 获取系统信息
      const systemInfo = await api.system.getInfo();
      console.log('📊 System info:', systemInfo);
      setSystemInfo(systemInfo);

      // 监听消息
      wsClient.on('pong', (msg) => {
        console.log('❤️ Heartbeat:', msg);
      });

      wsClient.on('step_update', (msg) => {
        console.log('📋 Step update:', msg);
        const stepData = msg.data;
        setCurrentStepIndex(stepData.step_index);
      });

      wsClient.on('chat_response', (msg) => {
        console.log('💬 Chat response:', msg);
        const data = msg.data;
        
        // 更新执行步骤
        if (data.steps && data.steps.length > 0) {
          setCurrentSteps(data.steps);
        } else {
          clearSteps();
        }

        // 追加助手回复
        if (data.text) {
          addMessage({ role: 'assistant', content: data.text });
        }
      });

      wsClient.on('thinking', () => {
        console.log('🤔 AI thinking...');
        clearSteps();
        setThinking(true);
      });
      wsClient.on('*', () => {
        // 任意消息到达后，取消思考状态
        setThinking(false);
      });
    } catch (error) {
      console.error('❌ Failed to initialize app:', error);
      setConnected(false);
    }
  };

  const sendTextCommand = async (text: string) => {
    // 先把用户消息落库
    addMessage({ role: 'user', content: text });

    // 临时强制HTTP，确保稳定（调试完再改回WS）
    try {
      console.log('[DEBUG] 发送HTTP请求:', text);
      setThinking(true);
      const resp = await api.chat.send(text);
      console.log('[DEBUG] 收到HTTP响应:', resp);
      setThinking(false);
      if (resp?.reply) {
        console.log('[DEBUG] 添加回复到UI:', resp.reply);
        addMessage({ role: 'assistant', content: resp.reply });
      } else {
        console.warn('[DEBUG] 响应无reply字段:', resp);
        addMessage({ role: 'system', content: '收到空回复，请重试' });
      }
      if (resp?.steps?.length) {
        setCurrentSteps(resp.steps);
      } else {
        clearSteps();
      }
      return;
    } catch (e: any) {
      console.error('[DEBUG] HTTP发送失败详情:', {
        message: e.message,
        response: e.response,
        config: e.config
      });
      setThinking(false);
      addMessage({ role: 'system', content: `请求失败: ${e.message || '未知错误'}` });
      return;
    }

    // 优先尝试WS，若短时间内未收到任何WS反馈，则自动HTTP兜底
    let wsAcknowledged = false;
    const onThinking = () => { wsAcknowledged = true; };
    const onChatResp = () => { wsAcknowledged = true; };
    wsClient.on('thinking', onThinking);
    wsClient.on('chat_response', onChatResp);

    const sent = wsClient.send({ type: 'chat', data: { text } });

    if (sent) {
      setTimeout(async () => {
        // 未获WS回执，走HTTP兜底
        if (!wsAcknowledged) {
          // 清理监听，避免重复触发
          wsClient.off('thinking', onThinking);
          wsClient.off('chat_response', onChatResp);
          try {
            setThinking(true);
            const resp = await api.chat.send(text);
            setThinking(false);
            if (resp?.reply) addMessage({ role: 'assistant', content: resp.reply });
            if (resp?.steps?.length) setCurrentSteps(resp.steps); else clearSteps();
          } catch (e) {
            setThinking(false);
            addMessage({ role: 'system', content: '抱歉，处理失败了，请重试' });
          }
        } else {
          // 已收到WS反馈，正常流程，移除一次性监听
          wsClient.off('thinking', onThinking);
          wsClient.off('chat_response', onChatResp);
        }
      }, 1200);
      return;
    }

    // WebSocket未连接时走HTTP兜底
    try {
      setThinking(true);
      const resp = await api.chat.send(text);
      setThinking(false);

      if (resp?.reply) {
        addMessage({ role: 'assistant', content: resp.reply });
      }
      if (resp?.steps?.length) {
        setCurrentSteps(resp.steps);
      } else {
        clearSteps();
      }
    } catch (e) {
      setThinking(false);
      addMessage({ role: 'system', content: '抱歉，处理失败了，请重试' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* 顶部状态栏 */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="text-3xl">🎤</div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                VoicePC
              </h1>
              <p className="text-xs text-gray-500">AI语音电脑助手</p>
            </div>
          </div>

          {/* 连接状态 */}
          <div className="flex items-center space-x-4">
            {/* Tab切换 */}
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  activeTab === 'chat'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }`}
              >
                💬 对话
              </button>
              <button
                onClick={() => setActiveTab('flow')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  activeTab === 'flow'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }`}
              >
                📊 流程
              </button>
            </div>

            <div className="flex items-center space-x-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-gray-600">
                {isConnected ? '已连接' : '未连接'}
              </span>
            {/* 调试用：显示WS地址 */}
            <span className="text-xs text-gray-400 hidden sm:inline-block">
              {wsClient.getUrl()}
            </span>
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-200px)]">
          {/* 左侧：动态面板 */}
          <div className="lg:col-span-2">
            {activeTab === 'chat' ? (
              <ChatPanel />
            ) : (
              <FlowVisualization steps={currentSteps} />
            )}
          </div>

          {/* 右侧：语音控制 */}
          <div className="flex flex-col">
            <div className="bg-white rounded-2xl shadow-lg p-8 flex-1 flex flex-col items-center justify-center">
              <VoiceButton />
              
              {/* 文字输入框 */}
              <div className="mt-6 w-full">
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    placeholder="或者在这里输入指令..."
                    className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:outline-none transition"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                        const text = e.currentTarget.value.trim();
                        sendTextCommand(text);
                        e.currentTarget.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={(e) => {
                      const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                      if (input && input.value.trim()) {
                        sendTextCommand(input.value.trim());
                        input.value = '';
                      }
                    }}
                    className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition font-medium"
                  >
                    发送
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-2 text-center">
                  输入后按回车或点击发送按钮
                </p>
              </div>

              {/* 功能说明 */}
              <div className="mt-12 w-full space-y-3">
                <h3 className="text-lg font-semibold text-gray-700 mb-4">
                  💡 试试这些指令
                </h3>
                {[
                  { cmd: '打开记事本', icon: '📝' },
                  { cmd: '搜索Python教程', icon: '🔍' },
                  { cmd: '播放音乐', icon: '🎵' },
                  { cmd: '准备工作', icon: '💼' },
                  { cmd: '音量调到50', icon: '🔊' },
                ].map((item) => (
                  <div
                    key={item.cmd}
                    className="bg-gradient-to-r from-blue-50 to-purple-50 px-4 py-3 rounded-lg text-sm text-gray-700 hover:shadow-md transition cursor-pointer"
                  >
                    <span className="mr-2">{item.icon}</span>
                    "{item.cmd}"
                  </div>
                ))}
              </div>

              {/* 状态提示 */}
              {currentSteps.length > 0 && (
                <div className="mt-6 w-full p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700 font-medium">
                    ✅ 已执行 {currentSteps.length} 个步骤
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* 底部信息 */}
      <footer className="text-center py-4 text-gray-500 text-sm">
        <p>VoicePC v1.0.0 - 校招比赛项目 | 核心功能就绪 🚀</p>
      </footer>
    </div>
  );
}

export default App;
