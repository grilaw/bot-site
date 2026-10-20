@echo off
start "Django" cmd /k "cd /d %~dp0 && call ..\.venv\Scripts\activate.bat && python manage.py runserver"
start "Vite" cmd /k "cd /d %~dp0school-pgs && call ..\..\.venv\Scripts\activate.bat && npm run dev"