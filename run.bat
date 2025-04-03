@echo off
chcp 65001 > nul
title PDF Toolkit Launcher

:: 顯示歡迎信息
cls
echo ========================================
echo         PDF Toolkit Launcher v0.2
echo ========================================
echo.

:: 設置變數
set "PYTHON_REQUIRED=0"
set "GS_REQUIRED=0"
set "POPPLER_REQUIRED=0"
set "ALL_OK=1"

:: 檢查Python
echo [1/4] 檢查Python安裝狀態...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo      [缺少] Python未安裝
    echo      請從 https://www.python.org/downloads/ 下載並安裝Python 3.8至3.13版本
    echo      安裝時請勾選"Add Python to PATH"選項
    set "PYTHON_REQUIRED=1"
    set "ALL_OK=0"
) else (
    echo      [已安裝] Python已安裝: 
    python --version
)
echo.

:: 檢查Ghostscript
echo [2/4] 檢查Ghostscript安裝狀態...
if exist "gs10.05.0\bin\gswin64c.exe" (
    echo      [已安裝] 已找到內置Ghostscript
) else (
    where gswin64c >nul 2>&1
    if %errorlevel% neq 0 (
        echo      [缺少] Ghostscript未安裝
        echo      請從 https://ghostscript.com/releases/gsdnld.html 下載並安裝Ghostscript
        echo      建議版本: Ghostscript 10.0.0或更新版本
        set "GS_REQUIRED=1"
        set "ALL_OK=0"
    ) else (
        echo      [已安裝] 系統Ghostscript已安裝
    )
)
echo.

:: 檢查Poppler
echo [3/4] 檢查Poppler安裝狀態...
where pdftoppm >nul 2>&1
if %errorlevel% neq 0 (
    echo      [缺少] Poppler未安裝
    echo      若要使用"舊版壓縮"功能，請安裝Poppler:
    echo      1. 從 https://github.com/oschwartz10612/poppler-windows/releases/ 下載
    echo      2. 解壓到指定目錄（如C:\Program Files\poppler）
    echo      3. 將bin目錄添加到系統PATH環境變數
    set "POPPLER_REQUIRED=1"
) else (
    echo      [已安裝] Poppler已安裝
)
echo.

:: 顯示安裝摘要
echo ========================================
if "%ALL_OK%"=="0" (
    echo [警告] 部分組件未安裝
    echo.
    if "%PYTHON_REQUIRED%"=="1" (
        echo 請安裝Python後再運行此程序
        echo 若已安裝Python，請確保其已添加到PATH環境變數中
    )
    if "%GS_REQUIRED%"=="1" (
        echo 若不安裝Ghostscript，某些PDF壓縮功能可能無法使用
    )
    echo.
    echo 請安裝所需組件後重新運行此程序
    echo 按任意鍵退出...
    pause >nul
    exit /b 1
)
if "%POPPLER_REQUIRED%"=="1" (
    echo [提示] Poppler未安裝
    echo 若不安裝Poppler，"舊版壓縮"功能將無法使用
    echo 其他功能不受影響
    echo.
)
echo [成功] 所有必要組件均已安裝
echo.

:: Install dependencies
echo [4/4] 安裝所需Python套件...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [嘗試安裝pip...]
    python -m ensurepip --upgrade >nul 2>&1
)

if exist requirements.txt (
    echo 從requirements.txt安裝依賴項...
    python -m pip install -r requirements.txt
) else (
    echo 安裝基本依賴項...
    python -m pip install streamlit PyPDF2 pikepdf pillow reportlab pdf2image
)
echo.

:run_app
:: Run the application
echo 啟動PDF工具箱...
if not exist app.py (
    echo [錯誤] 找不到app.py文件！
    echo 請確保您在正確的目錄中運行此腳本。
    goto ask_continue
)

echo 應用程序將在瀏覽器中打開。如果沒有自動打開，請訪問：
echo http://localhost:8501
echo.
echo [正在啟動應用程序，請稍候...]
echo (按Ctrl+C可終止應用程序)
echo.

streamlit run app.py

echo.
echo 應用程序已關閉。

:ask_continue
echo.
echo 您要退出嗎？
echo (輸入Y並按Enter退出，或輸入N並按Enter重新啟動應用程序)
set /p choice=選擇 (Y/N): 
if /i "%choice%"=="N" goto run_app

:exit
echo 感謝使用PDF工具箱！
echo 按任意鍵退出...
pause > nul
exit /b 0