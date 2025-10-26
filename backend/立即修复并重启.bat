@echo off
chcp 65001 >nul 2>&1
echo.
echo ========================================
echo     🚨 紧急修复并重启后端
echo ========================================
echo.

:: 1. 停止现有后端
echo [1/4] 停止现有后端进程...
taskkill /F /FI "WINDOWTITLE eq VoicePC Backend*" >nul 2>&1
taskkill /F /IM python.exe /FI "MEMUSAGE gt 50000" >nul 2>&1
timeout /t 2 >nul

:: 2. 确保.env配置正确
echo [2/4] 写入正确的API配置...
(
echo DEEPSEEK_API_KEY=sk-b9ea34c8c66f40369142f29a37a506a1
echo DEEPSEEK_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
echo DEEPSEEK_MODEL=qwen-turbo
echo APP_ENV=development
echo APP_HOST=0.0.0.0
echo APP_PORT=8000
echo LOG_LEVEL=INFO
echo LOG_FILE=logs/voicepc.log
) > .env

:: 3. 验证配置
echo [3/4] 验证配置...
python -c "from dotenv import load_dotenv; import os; load_dotenv(); key=os.getenv('DEEPSEEK_API_KEY'); print(f'API Key: {key[:20]}...' if key else 'NO KEY!')"

:: 4. 启动后端
echo [4/4] 启动后端...
echo.
echo ⚡ 后端正在启动，请查看启动日志...
echo 🔍 必须看到: AI Agent: READY (LangChain)
echo.
python run_backend.py

pause
