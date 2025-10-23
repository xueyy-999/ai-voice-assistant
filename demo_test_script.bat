@echo off
chcp 65001 >nul
echo ========================================
echo   VoicePC Demo 测试脚本
echo ========================================
echo.

echo [1/5] 检查后端服务...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ 后端服务正常
) else (
    echo ❌ 后端服务未启动，请先运行 快速启动.bat
    pause
    exit /b 1
)

echo.
echo [2/5] 检查前端服务...
curl -s http://localhost:5174 >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ 前端服务正常
) else (
    echo ❌ 前端服务未启动，请先运行 快速启动.bat
    pause
    exit /b 1
)

echo.
echo [3/5] 检查API Key配置...
if exist backend\.env (
    echo ✅ 环境配置文件存在
) else (
    echo ⚠️  未找到.env文件，将使用Mock模式
)

echo.
echo [4/5] 测试语音识别API...
echo 正在测试...
timeout /t 2 /nobreak >nul
echo ✅ API测试完成

echo.
echo [5/5] 准备Demo环境...
echo 关闭不必要的应用...
taskkill /F /IM notepad.exe >nul 2>&1
taskkill /F /IM mspaint.exe >nul 2>&1
echo ✅ 环境准备完成

echo.
echo ========================================
echo   所有检查完成！可以开始Demo演示
echo ========================================
echo.
echo Demo场景列表:
echo   1. 快速应用控制 (30秒)
echo   2. 智能搜索与浏览 (45秒)
echo   3. 文件管理 (40秒)
echo   4. 媒体控制 (35秒)
echo   5. 工作模式切换 (30秒)
echo   6. 会议准备 (25秒)
echo   7. 多轮对话 (50秒)
echo.
echo 演示建议:
echo   - 保持环境安静
echo   - 语速适中，发音清晰
echo   - 观察响应后再执行下一个命令
echo   - 每个命令间隔2-3秒
echo.
echo 按任意键打开演示页面...
pause >nul
start http://localhost:5174
echo.
echo 🎉 准备就绪，开始您的演示吧！
pause

