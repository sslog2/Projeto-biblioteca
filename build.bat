@echo off
setlocal EnableDelayedExpansion
chcp 65001 > nul
title Biblioteca - Build

echo ============================================
echo   Sistema de Biblioteca - Build Executavel
echo ============================================
echo.

REM ── Detecta ambiente CI (GitHub Actions define GITHUB_ACTIONS=true) ──────
if "%GITHUB_ACTIONS%"=="true" (
    set CI_MODE=1
) else (
    set CI_MODE=0
)

REM ── Verifica se Node.js está instalado ──────────────────────────────────
where node >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado. Instale em https://nodejs.org
    if "%CI_MODE%"=="0" pause
    exit /b 1
)

REM ── Seleciona Python: virtualenv (local) ou sistema (CI) ─────────────────
if "%CI_MODE%"=="1" (
    set PYTHON=python
    echo [INFO] Modo CI detectado - usando Python do sistema
) else (
    set PYTHON=env\Scripts\python.exe
    if not exist "!PYTHON!" (
        echo [ERRO] Virtualenv nao encontrado em env\
        echo        Execute: python -m venv env  ^&  env\Scripts\pip install -r requirements.txt
        pause & exit /b 1
    )
)

REM ── Passo 1: Instala PyInstaller ─────────────────────────────────────────
echo [1/5] Instalando PyInstaller...
%PYTHON% -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar PyInstaller
    if "%CI_MODE%"=="0" pause
    exit /b 1
)

REM ── Passo 2: Coleta arquivos estaticos ───────────────────────────────────
echo [2/5] Coletando arquivos estaticos (collectstatic)...
set DJANGO_SETTINGS_MODULE=project.settings
%PYTHON% manage.py collectstatic --noinput --clear 2>nul
if errorlevel 1 echo [AVISO] collectstatic retornou erro, continuando...

REM ── Passo 3: Empacota servidor Django com PyInstaller ────────────────────
echo [3/5] Empacotando servidor Django (PyInstaller)...
%PYTHON% -m PyInstaller biblioteca.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERRO] Falha no PyInstaller
    if "%CI_MODE%"=="0" pause
    exit /b 1
)

if not exist "dist\django_server\django_server.exe" (
    echo [ERRO] Executavel Django nao foi gerado em dist\django_server\
    if "%CI_MODE%"=="0" pause
    exit /b 1
)
echo       OK - dist\django_server\django_server.exe gerado

REM ── Passo 4: Instala dependencias Electron ───────────────────────────────
echo [4/5] Instalando dependencias Electron...
cd electron
if "%CI_MODE%"=="1" (
    call npm ci --prefer-offline
) else (
    call npm install --prefer-offline
)
if errorlevel 1 (
    echo [ERRO] npm install falhou
    cd ..
    if "%CI_MODE%"=="0" pause
    exit /b 1
)

REM ── Passo 5: Compila installer Windows ──────────────────────────────────
echo [5/5] Gerando instalador Windows...
set CSC_IDENTITY_AUTO_DISCOVERY=false
set WIN_CSC_LINK=
call npm run build:win
if errorlevel 1 (
    echo [ERRO] electron-builder falhou
    cd ..
    if "%CI_MODE%"=="0" pause
    exit /b 1
)
cd ..

echo.
echo ============================================
echo   Build concluido com sucesso!
echo   Instalador em: dist-electron\
echo ============================================
echo.
if "%CI_MODE%"=="0" (
    echo Para testar sem instalar:
    echo   cd electron ^&^& npm start
    echo.
    pause
)
