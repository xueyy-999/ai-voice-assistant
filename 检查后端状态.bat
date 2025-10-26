@echo off
chcp 65001 >nul
echo.
echo ========================================
echo     检查后端状态
echo ========================================
echo.

cd backend

echo [1/3] 检查API Key配置...
python -c "from app.config import settings; print('API Key:', 'OK' if settings.DEEPSEEK_API_KEY else 'MISSING')"

echo.
echo [2/3] 检查LangChain安装...
python -c "import langchain; print('LangChain:', 'OK')" 2>nul || echo LangChain: MISSING

echo.
echo [3/3] 检查最新日志（最后10行）...
powershell -Command "Get-Content logs\voicepc.log -Tail 10 -Encoding UTF8 2>$null"

echo.
echo ========================================
echo 如果看到 "AI Agent: READY" 说明正常
echo 如果看到 "SIMPLE MODE" 说明需要重启
echo ========================================
echo.
pause
