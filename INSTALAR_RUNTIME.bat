@echo off
title OptiCore Atletas v1.0 - Instalador
chcp 437 >nul
color 0B

set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

echo ===================================================
echo   OPTICORE ATLETAS v1.0 - INSTALADOR DE RUNTIME
echo   Crea el entorno Python portable en esta carpeta
echo ===================================================
echo.
echo Este proceso requiere conexion a Internet.
echo Tiempo estimado: 5-10 minutos.
echo.
pause

echo.
echo [1/5] Verificando Python del sistema...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python no encontrado en el sistema.
    echo Descarga Python 3.11 desde https://www.python.org/downloads/
    echo Marca "Add Python to PATH" al instalar, luego vuelve a ejecutar este archivo.
    echo.
    pause
    exit /b 1
)
python --version

echo.
echo [2/5] Creando entorno virtual en runtime...
if exist "runtime\" (
    echo    Eliminando runtime anterior...
    rmdir /s /q runtime
)
python -m venv runtime
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual.
    pause
    exit /b 1
)
echo    Entorno creado.

echo.
echo [3/5] Actualizando pip...
runtime\Scripts\python.exe -m pip install --upgrade pip --quiet --no-warn-script-location

echo.
echo [4/5] Instalando paquetes...
echo.

echo    fastapi + uvicorn...
runtime\Scripts\pip.exe install fastapi "uvicorn[standard]" --quiet --no-warn-script-location
if errorlevel 1 goto :error

echo    pydantic...
runtime\Scripts\pip.exe install pydantic --quiet --no-warn-script-location
if errorlevel 1 goto :error

echo    numpy + scipy (solver HiGHS)...
runtime\Scripts\pip.exe install numpy scipy --quiet --no-warn-script-location
if errorlevel 1 goto :error

echo    streamlit...
runtime\Scripts\pip.exe install streamlit --quiet --no-warn-script-location
if errorlevel 1 goto :error

echo    requests + pandas...
runtime\Scripts\pip.exe install requests pandas --quiet --no-warn-script-location
if errorlevel 1 goto :error

echo    plotly + openpyxl...
runtime\Scripts\pip.exe install plotly openpyxl --quiet --no-warn-script-location
if errorlevel 1 goto :error

echo.
echo [5/5] Verificando instalacion...
runtime\Scripts\python.exe -c "import fastapi, uvicorn, pydantic, numpy, scipy, streamlit, requests, pandas, plotly, openpyxl; print('   Todos los paquetes instalados correctamente')"
if errorlevel 1 goto :error

echo.
echo ===================================================
echo   INSTALACION COMPLETADA
echo   Ya puedes ejecutar INICIAR.bat
echo ===================================================
echo.
pause
exit /b 0

:error
echo.
echo ERROR: Fallo en la instalacion de un paquete.
echo Verifica tu conexion a Internet y vuelve a intentarlo.
echo.
pause
exit /b 1
