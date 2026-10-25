@echo off
title Wanderlust AI Travel Planner
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"
pause
