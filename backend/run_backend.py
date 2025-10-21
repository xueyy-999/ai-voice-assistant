#!/usr/bin/env python
"""后端启动脚本"""
import sys
import os

# 添加backend目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 启动应用
from app.main import start_server

if __name__ == "__main__":
    start_server()
