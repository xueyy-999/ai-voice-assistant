# VoicePC 安装指南

## 📋 系统要求

- **操作系统**: Windows 10/11
- **Node.js**: 18.x 或更高版本
- **Python**: 3.10 或更高版本
- **内存**: 8GB RAM 及以上
- **磁盘空间**: 至少 2GB 可用空间

---

## 🔧 环境准备

### 1. 安装 Node.js

访问 [Node.js官网](https://nodejs.org/) 下载并安装 18.x LTS 版本

验证安装：
```bash
node --version  # 应显示 v18.x.x
npm --version   # 应显示 9.x.x 或更高
```

### 2. 安装 Python

访问 [Python官网](https://www.python.org/) 下载并安装 3.10+ 版本

**重要**: 安装时勾选 "Add Python to PATH"

验证安装：
```bash
python --version  # 应显示 Python 3.10.x 或更高
pip --version     # 应显示 pip 23.x.x 或更高
```

### 3. 安装 Git（可选）

如果需要克隆仓库：
```bash
git --version  # 验证 Git 已安装
```

---

## 📦 项目安装

### 方式一：使用本地项目

1. **进入项目目录**
```bash
cd D:\校招比赛
```

2. **安装后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

可能需要等待 5-10 分钟，取决于网络速度。

3. **安装前端依赖**
```bash
cd ../frontend
npm install
```

可能需要等待 5-10 分钟。

---

## 🔑 配置 API 密钥

### 1. 获取 DeepSeek API Key

1. 访问 [DeepSeek开放平台](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入控制台 → API Keys
4. 点击"创建新的 API Key"
5. 复制生成的 API Key

**免费额度**: 500万 tokens（足够开发和演示使用）

### 2. 获取阿里云语音服务

1. 访问 [阿里云智能语音](https://ai.aliyun.com/nls)
2. 开通"智能语音交互"服务
3. 创建项目并获取：
   - AppKey
   - AccessKey ID
   - AccessKey Secret

**免费额度**: 新用户免费 3 个月

### 3. 配置环境变量

在 `backend/` 目录下创建 `.env` 文件：

```bash
cd backend
copy .env.example .env
```

编辑 `.env` 文件，填入你的密钥：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxx

# 阿里云语音配置
ALI_APPKEY=your_appkey_here
ALI_ACCESS_KEY=your_access_key_here
ALI_SECRET_KEY=your_secret_key_here

# 其他配置保持默认即可
```

---

## 🚀 启动应用

### 1. 启动后端服务

打开 **PowerShell 或 CMD 窗口 1**：

```bash
cd D:\校招比赛\backend
python app/main.py
```

看到以下信息表示启动成功：
```
🚀 VoicePC Backend starting...
✅ Database initialized
🌐 Starting server on 0.0.0.0:8000
```

### 2. 启动前端应用

打开 **PowerShell 或 CMD 窗口 2**：

```bash
cd D:\校招比赛\frontend
npm run dev -- --port 5174
```

看到以下信息表示启动成功：
```
VITE v5.0.5  ready in 1234 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 3. 访问应用

在浏览器中打开：**http://localhost:5174/**

你应该看到 VoicePC 的欢迎界面！

---

## 🐛 常见问题排查

### 问题 1: `pip install` 失败

**症状**: 安装 Python 依赖时报错

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 2: `npm install` 卡住不动

**症状**: 安装 Node 依赖时长时间无响应

**解决方案**:
```bash
# 切换到淘宝镜像源
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install
```

### 问题 3: 端口被占用

**症状**: `Error: listen EADDRINUSE: address already in use :::8000`

**解决方案**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程（替换 PID 为实际进程号）
taskkill /PID <PID> /F
```

### 问题 4: Python 命令找不到

**症状**: `'python' 不是内部或外部命令`

**解决方案**:
- 使用 `python3` 或 `py` 命令
- 或重新安装 Python，勾选 "Add to PATH"

### 问题 5: 后端启动报错

**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 确认在正确的目录
cd backend

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

---

## 📝 验证安装

访问以下地址验证各服务：

- **后端健康检查**: http://localhost:8000/health
  - 应返回: `{"status":"ok"}`

- **后端 API 文档**: http://localhost:8000/docs
  - 可以看到所有 API 接口

- **前端应用**: http://localhost:5174/
  - 可以看到 VoicePC 界面

---

## 🎉 安装成功！

如果以上步骤都完成且无报错，恭喜你已经成功安装 VoicePC！

接下来可以：
1. 查看 [用户手册](USER_GUIDE.md) 学习如何使用
2. 测试语音识别功能
3. 体验 AI 语音控制

---

## 🆘 获取帮助

如果遇到其他问题：
1. 查看日志文件: `backend/logs/voicepc.log`
2. 检查环境变量配置是否正确
3. 确认防火墙未阻止应用运行

---

**祝你使用愉快！** 🚀

