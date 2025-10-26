@echo off
chcp 65001 >nul 2>&1
echo.
echo ========================================
echo     🚨 强制修复并启动
echo ========================================
echo.

:: 强制杀死所有Python进程
echo [1/3] 杀死所有Python进程...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

:: 验证API Key
echo [2/3] 验证配置...
python -c "import sys; sys.path.insert(0, '.'); from app.config import settings; print(f'API Key: {settings.DEEPSEEK_API_KEY[:20]}...' if settings.DEEPSEEK_API_KEY else 'NO KEY!')"

:: 启动
echo [3/3] 启动后端...
echo.
echo 🔍 必须看到: AI Agent: READY (LangChain)
echo.
python run_backend.py
