# VoicePC - AI语音电脑助手

<div align="center">

**用自然语言语音控制你的Windows电脑**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-18.x-green.svg)](https://nodejs.org/)

</div>

---

## 🎯 项目简介

VoicePC是一个基于大模型的智能语音电脑助手，让你可以用自然语言控制Windows电脑：
- 🎤 **语音交互**: 实时语音识别和自然语言理解
- 🤖 **智能决策**: AI自动理解意图并规划任务步骤
- 🛠️ **系统控制**: 控制应用、文件、浏览器、多媒体
- 📊 **可视化**: 实时展示AI的思考和执行过程
- 🔗 **任务编排**: 组合多个能力完成复杂场景

---

## ✨ 核心功能

### 基础控制能力
- 📱 **应用控制**: "打开微信"、"关闭浏览器"
- 📁 **文件操作**: "打开D盘下的项目文档"、"创建一个新文件夹"
- 🌐 **浏览器**: "打开百度搜索Python教程"
- 📝 **文本处理**: "创建一个文档，写入今天的计划"
- 🎵 **多媒体**: "播放音乐"、"音量调到50%"

### 智能场景
- 💼 **准备工作**: 自动打开VS Code、浏览器、播放背景音乐
- ✍️ **创作模式**: 打开文档编辑器、搜索资料、生成大纲

---

## 🚀 快速开始

### 环境要求
- Windows 10/11
- Node.js 18.x+
- Python 3.10+
- 8GB+ RAM

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/xueyy-999/ai-voice-assistant.git
cd ai-voice-assistant
```

#### 2. 后端安装
```bash
cd backend
pip install -r requirements.txt
```

#### 3. 前端安装
```bash
cd ../frontend
npm install
```

#### 4. 配置环境变量
复制 `.env.example` 为 `.env`，填入你的API密钥：
```bash
# 后端配置
cd backend
cp .env.example .env

# 编辑 .env 文件
# DEEPSEEK_API_KEY=your_deepseek_api_key
# ALI_APPKEY=your_ali_appkey
```

#### 5. 启动应用

**终端1 - 启动后端**:
```bash
cd backend
python app/main.py
```

**终端2 - 启动前端**:
```bash
cd frontend
npm run dev
```

---

## 📖 使用指南

### 基础使用
1. 启动应用后，点击麦克风按钮（或按住空格键）
2. 说出你的指令，如"打开微信"
3. 松开按钮，AI会理解并执行你的指令

### 示例指令
```
"打开微信"
"搜索Python教程"
"创建一个名为test的文档"
"播放音乐并调低音量"
"准备工作" (执行预设场景)
```

---

## 🏗️ 项目结构

```
voicepc/
├── frontend/          # Electron + React前端
│   ├── src/
│   │   ├── main/      # Electron主进程
│   │   ├── renderer/  # React渲染进程
│   │   └── preload/   # 预加载脚本
│   └── package.json
├── backend/           # Python FastAPI后端
│   ├── app/
│   │   ├── api/       # API路由
│   │   ├── services/  # 业务服务
│   │   ├── tools/     # 工具插件
│   │   └── main.py    # 入口文件
│   └── requirements.txt
├── docs/              # 项目文档
└── README.md
```

---

## 🔑 API密钥获取

### DeepSeek API (免费500万tokens)
1. 访问 [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. 注册账号
3. 创建API Key

### 阿里云语音 (新用户免费3个月)
1. 访问 [https://ai.aliyun.com/nls](https://ai.aliyun.com/nls)
2. 开通智能语音交互服务
3. 获取AppKey和AccessKey

---

## 🛠️ 技术栈

### 前端
- Electron 28.x
- React 18
- TypeScript
- TailwindCSS
- Zustand

### 后端
- Python 3.10
- FastAPI
- LangChain
- SQLite

### AI服务
- DeepSeek (大模型)
- 阿里云智能语音 (STT/TTS)

---

## 📋 开发计划

- [x] 项目设计完成
- [ ] Phase 1: 基础设施搭建
- [ ] Phase 2: 语音服务模块
- [ ] Phase 3: AI决策模块
- [ ] Phase 4: 工具插件模块
- [ ] Phase 5: 前端界面模块
- [ ] Phase 6: 集成测试与优化

详见 [TASK文档](docs/AI语音控制助手/TASK_AI语音控制助手.md)

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

## 👨‍💻 作者

校招比赛项目 - 2025

---

## 🙏 致谢

- DeepSeek - 提供强大的大模型能力
- 阿里云 - 提供语音识别和合成服务
- LangChain - 提供Agent框架

---

**⚡ 让AI成为你的桌面助手！**

