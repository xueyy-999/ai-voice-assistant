# VoicePC API 文档

## 📋 概述

VoicePC后端提供RESTful API和WebSocket接口，用于语音识别、对话交互和系统控制。

**基础URL**: `http://localhost:8000/api`

---

## 🎤 语音服务 API

### 1. 语音识别

**POST** `/voice/recognize`

将音频数据转换为文本。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| audio_file | File | 是 | 音频文件（支持WAV、MP3、PCM） |
| format | string | 否 | 音频格式，默认wav |
| sample_rate | integer | 否 | 采样率，默认16000 |

#### 请求示例

```bash
curl -X POST http://localhost:8000/api/voice/recognize \
  -F "audio_file=@recording.wav" \
  -F "format=wav"
```

#### 响应示例

```json
{
  "text": "打开微信",
  "confidence": 0.95,
  "duration": 1.2
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|-----|------|------|
| text | string | 识别出的文本 |
| confidence | float | 置信度（0-1） |
| duration | float | 音频时长（秒） |

---

### 2. 语音合成

**POST** `/voice/synthesize`

将文本转换为语音。

#### 请求参数

```json
{
  "text": "你好，我是VoicePC",
  "voice": "female",
  "speed": 1.0,
  "pitch": 1.0
}
```

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| text | string | 是 | 要合成的文本 |
| voice | string | 否 | 语音类型：female/male，默认female |
| speed | float | 否 | 语速（0.5-2.0），默认1.0 |
| pitch | float | 否 | 音调（0.5-2.0），默认1.0 |

#### 响应

返回音频二进制数据（MP3格式）

```
Content-Type: audio/mpeg
```

---

## 💬 对话服务 API

### 3. 发送对话消息

**POST** `/chat/send`

发送对话消息，获取AI回复和执行结果。

#### 请求参数

```json
{
  "message": "打开微信",
  "session_id": "uuid-xxxx-xxxx"
}
```

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| message | string | 是 | 用户消息 |
| session_id | string | 否 | 会话ID，不提供则自动创建 |

#### 响应示例

```json
{
  "session_id": "uuid-xxxx-xxxx",
  "reply": "好的，正在为您打开微信",
  "steps": [
    {
      "tool": "AppControlTool",
      "action": "open_app",
      "input": {
        "app_name": "微信"
      },
      "result": "成功打开微信",
      "status": "success"
    }
  ],
  "timestamp": 1698123456
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|-----|------|------|
| session_id | string | 会话ID |
| reply | string | AI回复文本 |
| steps | array | 执行步骤列表 |
| timestamp | integer | 时间戳 |

---

### 4. 获取对话历史

**GET** `/chat/history?session_id={session_id}&limit={limit}`

获取指定会话的历史记录。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| session_id | string | 是 | 会话ID |
| limit | integer | 否 | 返回数量，默认50 |

#### 响应示例

```json
{
  "messages": [
    {
      "role": "user",
      "content": "打开微信",
      "timestamp": 1698123456
    },
    {
      "role": "assistant",
      "content": "好的，正在为您打开微信",
      "timestamp": 1698123457
    }
  ]
}
```

---

### 5. WebSocket实时对话

**WebSocket** `/chat/ws`

建立WebSocket连接，支持实时双向通信。

#### 连接示例

```javascript
const ws = new WebSocket('ws://localhost:8000/api/chat/ws');

ws.onopen = () => {
  console.log('WebSocket连接已建立');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('收到消息:', message);
};
```

#### 消息格式

**客户端 → 服务器**

```json
{
  "type": "chat",
  "data": {
    "text": "打开微信"
  }
}
```

**服务器 → 客户端**

1. **思考中状态**
```json
{
  "type": "thinking",
  "data": {
    "status": "processing"
  }
}
```

2. **执行步骤更新**
```json
{
  "type": "step_update",
  "data": {
    "step_index": 0,
    "tool": "AppControlTool",
    "status": "completed",
    "result": "成功打开微信"
  }
}
```

3. **最终回复**
```json
{
  "type": "response",
  "data": {
    "text": "好的，已经为您打开微信",
    "steps": [...]
  }
}
```

4. **心跳消息**
```json
{
  "type": "ping"
}
```

响应：
```json
{
  "type": "pong",
  "timestamp": 1698123456
}
```

---

## ⚙️ 任务服务 API

### 6. 执行任务

**POST** `/task/execute`

直接执行指定的任务。

#### 请求参数

```json
{
  "task_type": "open_app",
  "parameters": {
    "app_name": "微信"
  }
}
```

#### 响应示例

```json
{
  "task_id": "task-xxxx",
  "status": "success",
  "result": "成功打开微信",
  "execution_time": 0.8
}
```

---

### 7. 获取任务状态

**GET** `/task/status/{task_id}`

查询任务执行状态。

#### 响应示例

```json
{
  "task_id": "task-xxxx",
  "status": "completed",
  "progress": 100,
  "result": "任务已完成"
}
```

---

## 🔧 系统服务 API

### 8. 健康检查

**GET** `/system/health`

检查服务健康状态。

#### 响应示例

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "services": {
    "voice": "ok",
    "ai": "ok",
    "database": "ok"
  }
}
```

---

### 9. 获取系统信息

**GET** `/system/info`

获取系统信息。

#### 响应示例

```json
{
  "os": "Windows",
  "version": "11",
  "python_version": "3.10.0",
  "available_tools": [
    "AppControlTool",
    "FileOperationTool",
    "BrowserControlTool",
    "MediaControlTool",
    "TextProcessingTool"
  ]
}
```

---

## 📊 错误码说明

### HTTP状态码

| 状态码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 业务错误码

```json
{
  "error": {
    "code": "VOICE_RECOGNITION_FAILED",
    "message": "语音识别失败",
    "details": "音频格式不支持"
  }
}
```

| 错误码 | 说明 |
|-------|------|
| VOICE_RECOGNITION_FAILED | 语音识别失败 |
| VOICE_SYNTHESIS_FAILED | 语音合成失败 |
| AI_SERVICE_ERROR | AI服务错误 |
| TOOL_EXECUTION_FAILED | 工具执行失败 |
| INVALID_SESSION | 无效的会话ID |
| RATE_LIMIT_EXCEEDED | 请求频率超限 |

---

## 🔐 认证与授权

当前版本为本地开发版本，暂未实现认证机制。

生产环境建议：
- 使用API Key认证
- 实现OAuth 2.0
- 添加请求频率限制

---

## 📝 使用示例

### Python示例

```python
import requests

# 语音识别
with open('audio.wav', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/voice/recognize',
        files={'audio_file': f}
    )
    result = response.json()
    print(f"识别结果: {result['text']}")

# 发送对话
response = requests.post(
    'http://localhost:8000/api/chat/send',
    json={
        'message': '打开微信'
    }
)
result = response.json()
print(f"AI回复: {result['reply']}")
```

### JavaScript示例

```javascript
// 语音识别
const formData = new FormData();
formData.append('audio_file', audioBlob);

const response = await fetch('http://localhost:8000/api/voice/recognize', {
  method: 'POST',
  body: formData
});
const result = await response.json();
console.log('识别结果:', result.text);

// WebSocket连接
const ws = new WebSocket('ws://localhost:8000/api/chat/ws');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'response') {
    console.log('AI回复:', message.data.text);
  }
};

ws.send(JSON.stringify({
  type: 'chat',
  data: { text: '打开微信' }
}));
```

---

## 🚀 性能优化建议

1. **批量请求**: 合并多个请求减少网络开销
2. **缓存**: 对常见查询结果进行缓存
3. **压缩**: 启用gzip压缩减少传输数据量
4. **连接复用**: WebSocket保持长连接
5. **异步处理**: 对耗时操作使用异步接口

---

## 📞 技术支持

- GitHub Issues: https://github.com/xueyy-999/ai-voice-assistant/issues
- 文档更新时间: 2025年10月22日
