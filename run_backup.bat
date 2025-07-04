@echo off
chcp 65001 >nul
echo 正在启动智能备份脚本...
echo 当前时间: %date% %time%

cd /d "%~dp0"
python tier_backup.py

if %errorlevel% equ 0 (
    echo 备份脚本执行完成
) else (
    echo 备份脚本执行失败，错误代码: %errorlevel%
    pause
) 