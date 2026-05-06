@echo off
chcp 65001 >nul
echo 启动暗标格式检查工具...
echo 访问地址: http://localhost:8001
echo 按 Ctrl+C 停止服务
echo.
cd /d "%~dp0backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8001
