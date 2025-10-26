@echo off
chcp 65001 >nul
title VoicePC - 快速启动

echo.
echo ========================================
echo    VoicePC - AI语音电脑助手
echo ========================================
echo.

echo [1/3] 检查环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

echo ✅ Python 和 Node.js 已安装

echo.
echo [2/3] 启动后端服务...
start "VoicePC Backend" cmd /k "cd backend && python run_backend.py"

timeout /t 3 /nobreak >nul

echo.
echo [3/3] 启动前端应用...
start "VoicePC Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo ✅ VoicePC 正在启动...
echo.
echo 后端服务: http://localhost:8000
echo 前端应用: http://localhost:5174
echo.
echo 请等待约 10-30 秒让服务完全启动
echo ========================================
echo.

timeout /t 5 /nobreak >nul
start http://localhost:5174

echo 浏览器已打开，如未自动打开请手动访问:
echo http://localhost:5174
echo.
echo 按任意键关闭此窗口...
pause >nul

