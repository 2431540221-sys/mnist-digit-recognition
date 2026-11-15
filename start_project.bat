@echo off
title Khoi dong MNIST Web
echo Dang khoi dong Backend (Flask)...
start "MNIST Backend (Flask)" cmd /k "cd /d %~dp0mnist-web\backend && C:\Users\luuki\AppData\Local\Programs\Python\Python312\python.exe app.py"

echo Dang khoi dong Frontend (Vite)...
start "MNIST Frontend (Vite)" cmd /k "cd /d %~dp0mnist-web\frontend && npm run dev"

echo.
echo ========================================================
echo Backend va Frontend da duoc khoi dong trong 2 cua so moi!
echo Frontend: http://localhost:5173
echo Backend:  http://127.0.0.1:5000
echo ========================================================
pause
