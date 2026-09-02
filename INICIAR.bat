@echo off
title OptiCore Atletas v1.0
chcp 65001 >nul
color 0A

set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1

if not exist "runtime\Scripts\python.exe" (
    echo ERROR: No se encuentra el entorno 'runtime'.
    echo Asegurate de descomprimir la carpeta completa.
    pause
    exit
)

echo ==========================================
echo    OPTICORE ATLETAS v1.0
echo    Dieta Personalizada de Precision
echo    Iniciando sistema...
echo ==========================================
echo.

echo [1/3] Levantando motor matematico (FastAPI)...
start "" /min cmd /c "runtime\Scripts\uvicorn app:app --host 127.0.0.1 --port 8000"

echo [2/3] Esperando respuesta del servidor API...
timeout /t 4 /nobreak >nul

echo [3/3] Iniciando Dashboard (Streamlit)...
start "" /min cmd /c "runtime\Scripts\streamlit run consultant_workspace.py --server.port 8502 --server.headless true --browser.gatherUsageStats false --server.address 127.0.0.1"

echo    Esperando compilacion del frontend...
timeout /t 8 /nobreak >nul

echo Abriendo navegador...
start http://127.0.0.1:8502

echo.
echo ==========================================
echo  OptiCore Atletas iniciado correctamente.
echo  Cierra esta ventana para detener todo.
echo ==========================================
echo.
pause

echo.
echo Cerrando servicios...
taskkill /F /IM uvicorn.exe /T 2>nul
echo OptiCore detenido.
pause
