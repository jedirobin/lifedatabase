@echo off
chcp 65001 > nul
title GrabLab 爬虫Web控制台

echo ==============================================
echo    GrabLab 智能多平台爬虫系统
echo    Web界面启动中...
echo ==============================================
echo.

cd /d "%~dp0"
python webui.py

echo.
echo 按任意键退出...
pause > nul
