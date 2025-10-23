@echo off
chcp 65001 >nul
cls
echo ========================================
echo   VoicePC 项目启动
echo ========================================
echo.

echo [1/3] 检查环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未加入PATH
    pause
    exit /b 1
)
echo ✅ Python环境正常

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装或未加入PATH
    pause
    exit /b 1
)
echo ✅ Node.js环境正常

echo.
echo [2/3] 启动后端服务...
cd backend
start "VoicePC-Backend" cmd /k "python run_backend.py"
echo ✅ 后端服务启动中...
cd ..

echo.
echo [3/3] 启动前端服务...
cd frontend
start "VoicePC-Frontend" cmd /k "npm run dev"
echo ✅ 前端服务启动中...
cd ..

echo.
echo ========================================
echo   服务启动中，请稍候...
echo ========================================
echo.
echo 等待5秒后自动打开浏览器...
timeout /t 5 /nobreak >nul

echo.
echo 打开浏览器...
start http://localhost:5174

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 📌 访问地址:
echo    前端: http://localhost:5174
echo    后端: http://localhost:8000
echo.
echo 📌 如何使用:
echo    1. 等待页面加载完成
echo    2. 允许麦克风权限
echo    3. 按住中间的大按钮说话
echo    4. 或按住空格键说话
echo.
echo 📌 测试指令:
echo    - "你好"
echo    - "打开微信"
echo    - "搜索Python教程"
echo.
echo 如需关闭服务，请关闭对应的命令行窗口
echo.
pause

