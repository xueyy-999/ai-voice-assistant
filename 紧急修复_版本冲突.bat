@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   🚨 修复LangChain版本冲突
echo ========================================
echo.

cd backend

echo [1/2] 卸载所有LangChain相关包...
pip uninstall -y langchain langchain-core langchain-openai langchain-community langchain-text-splitters langchain-classic langgraph langgraph-checkpoint langgraph-prebuilt langgraph-sdk langsmith 2>nul

echo.
echo [2/2] 重新安装兼容版本...
pip install langchain==0.1.0 langchain-openai==0.0.2 langchain-community==0.0.10

echo.
echo ========================================
echo ✅ 修复完成！请重启后端测试
echo ========================================
pause
