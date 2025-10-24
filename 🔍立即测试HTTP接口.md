# 🔍 立即测试 HTTP 接口

**发现**: 后端已经正确回复，但前端WebSocket没收到！  
**解决**: 先测试HTTP接口，确认后端正常

---

## 🚀 方法1: 浏览器测试（最快）

### 第1步: 打开API文档
```
http://localhost:8000/docs
```

### 第2步: 找到 POST /api/chat/send
1. 滚动到 "chat" 部分
2. 找到 `POST /api/chat/send`
3. 点击展开

### 第3步: 点击 "Try it out"
点击右侧的 "Try it out" 按钮

### 第4步: 输入测试数据
```json
{
  "message": "你好",
  "session_id": "test-123"
}
```

### 第5步: 点击 "Execute"
看 Response body 里是否有 `reply` 字段

---

## ✅ 预期结果

```json
{
  "session_id": "test-123",
  "reply": "你好，我在。可以试试：'打开记事本'、'搜索Python教程'、'音量调到50'。",
  "steps": [],
  "success": true
}
```

---

## 🐛 如果HTTP能回复，说明问题在前端WebSocket

需要修复前端WebSocket接收逻辑。

---

## 📝 PowerShell 测试（备选）

```powershell
$body = @{
    message = "你好"
    session_id = "test-456"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/chat/send" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

---

**现在立即打开 http://localhost:8000/docs 测试！** 🚀

