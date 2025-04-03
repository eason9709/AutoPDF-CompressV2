#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform
import pkg_resources
import webbrowser
import time
import shutil
from pathlib import Path

# 設置控制台為UTF-8編碼
if platform.system() == "Windows":
    os.system("chcp 65001 > nul")

print("=" * 40)
print("      PDF工具箱啟動器 v0.2")
print("=" * 40)
print()

def print_color(text, color="white"):
    """輸出彩色文字"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def run_command(command, silent=False):
    """執行命令並返回結果"""
    try:
        if silent:
            result = subprocess.run(
                command, shell=True, check=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        else:
            result = subprocess.run(command, shell=True, check=False, text=True)
        return result.returncode == 0, result.stdout if silent else ""
    except Exception as e:
        print_color(f"執行命令時出錯: {e}", "red")
        return False, ""

def check_python():
    """檢查Python版本"""
    print_color("[1/4] 檢查Python安裝狀態...", "blue")
    
    version = sys.version.split()[0]
    print_color(f"      [已安裝] Python版本: {version}", "green")
    
    major, minor = map(int, version.split(".")[:2])
    if major != 3 or minor < 8 or minor > 13:
        print_color(f"      [警告] 建議使用Python 3.8 ~ 3.12版本，當前版本{version}可能存在兼容性問題", "yellow")
        print_color("      如遇問題，請考慮安裝推薦版本: https://www.python.org/downloads/", "yellow")
    
    return True

def check_ghostscript():
    """檢查Ghostscript安裝"""
    print_color("[2/4] 檢查Ghostscript安裝狀態...", "blue")
    
    # 檢查內置Ghostscript
    if os.path.exists("gs10.05.0/bin/gswin64c.exe"):
        print_color("      [已安裝] 已找到內置Ghostscript", "green")
        return True
    
    # 檢查系統Ghostscript
    is_installed = False
    
    if platform.system() == "Windows":
        is_installed, output = run_command("where gswin64c", True)
    else:  # macOS or Linux
        is_installed, output = run_command("which gs", True)
    
    if is_installed:
        print_color("      [已安裝] 系統Ghostscript已安裝", "green")
        return True
    else:
        print_color("      [缺少] Ghostscript未安裝", "yellow")
        print_color("      請從 https://ghostscript.com/releases/gsdnld.html 下載並安裝Ghostscript", "yellow")
        print_color("      建議版本: Ghostscript 10.0.0或更新版本", "yellow")
        print_color("      (如不安裝，某些PDF壓縮功能可能無法使用)", "yellow")
        return False

def check_poppler():
    """檢查Poppler安裝"""
    print_color("[3/4] 檢查Poppler安裝狀態...", "blue")
    
    is_installed = False
    
    if platform.system() == "Windows":
        is_installed, output = run_command("where pdftoppm", True)
    else:  # macOS or Linux
        is_installed, output = run_command("which pdftoppm", True)
    
    if is_installed:
        print_color("      [已安裝] Poppler已安裝", "green")
        return True
    else:
        print_color("      [缺少] Poppler未安裝", "yellow")
        print_color("      若要使用「舊版壓縮」功能，請安裝Poppler:", "yellow")
        
        if platform.system() == "Windows":
            print_color("      1. 從 https://github.com/oschwartz10612/poppler-windows/releases/ 下載", "yellow")
            print_color("      2. 解壓到指定目錄（如C:\\Program Files\\poppler）", "yellow")
            print_color("      3. 將bin目錄添加到系統PATH環境變數", "yellow")
        elif platform.system() == "Darwin":  # macOS
            print_color("      運行: brew install poppler", "yellow")
        else:  # Linux
            print_color("      運行: sudo apt install poppler-utils", "yellow")
        
        print_color("      (如不安裝，「舊版壓縮」功能將無法使用，其他功能不受影響)", "yellow")
        return False

def install_dependencies():
    """安裝所需依賴"""
    print_color("[4/4] 安裝所需Python套件...", "blue")
    
    # 檢查pip
    is_pip_installed, _ = run_command(f"{sys.executable} -m pip --version", True)
    if not is_pip_installed:
        print_color("      [安裝pip] pip未安裝，嘗試安裝...", "yellow")
        run_command(f"{sys.executable} -m ensurepip --upgrade")
    
    # 要安裝的套件列表
    required_packages = [
        "streamlit",
        "PyPDF2",
        "pikepdf",
        "pillow",
        "reportlab",
        "pdf2image"
    ]
    
    # 檢查是否存在requirements.txt
    if os.path.exists("requirements.txt"):
        print_color("      從requirements.txt安裝依賴項...", "blue")
        success, _ = run_command(f"{sys.executable} -m pip install -r requirements.txt")
        if not success:
            print_color("      從requirements.txt安裝失敗，嘗試安裝基本依賴...", "yellow")
            for package in required_packages:
                print_color(f"      安裝 {package}...", "blue")
                run_command(f"{sys.executable} -m pip install {package}")
    else:
        print_color("      安裝基本依賴項...", "blue")
        for package in required_packages:
            print_color(f"      安裝 {package}...", "blue")
            run_command(f"{sys.executable} -m pip install {package}")
    
    print_color("      依賴項安裝完成", "green")
    return True

def launch_app():
    """啟動應用程序"""
    if not os.path.exists("app.py"):
        print_color("[錯誤] 找不到app.py文件！", "red")
        print_color("請確保您在正確的目錄中運行此腳本。", "red")
        return False
    
    print_color("\n啟動PDF工具箱...", "green")
    print_color("應用程序將在瀏覽器中打開。如果沒有自動打開，請訪問：", "blue")
    print_color("http://localhost:8501", "cyan")
    print_color("\n[正在啟動應用程序，請稍候...]", "blue")
    print_color("(按Ctrl+C可終止應用程序)\n", "yellow")
    
    try:
        # 嘗試導入streamlit以確保已安裝
        import streamlit
        
        # 啟動應用
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待應用啟動
        time.sleep(2)
        
        # 如果沒有出錯，返回True
        return True
    except ImportError:
        print_color("[錯誤] 未安裝streamlit，請重新運行安裝腳本", "red")
        return False
    except Exception as e:
        print_color(f"[錯誤] 啟動應用時出錯: {e}", "red")
        return False

def main():
    """主函數"""
    # 檢查環境
    python_ok = check_python()
    gs_ok = check_ghostscript()
    poppler_ok = check_poppler()
    print()
    
    # 安裝依賴
    deps_ok = install_dependencies()
    print()
    
    # 環境檢查摘要
    print_color("=" * 40, "cyan")
    if not python_ok:
        print_color("[錯誤] Python環境檢查失敗", "red")
        input("按Enter鍵退出...")
        return
    
    if not gs_ok:
        print_color("[警告] Ghostscript未安裝，某些壓縮功能可能受限", "yellow")
    
    if not poppler_ok:
        print_color("[警告] Poppler未安裝，「舊版壓縮」功能將不可用", "yellow")
    
    if deps_ok:
        print_color("[成功] 所有必要依賴已安裝", "green")
    else:
        print_color("[警告] 部分依賴安裝可能失敗", "yellow")
    
    print()
    
    # 啟動應用
    try:
        app_launched = launch_app()
        if app_launched:
            # 等待應用程序終止
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print_color("\n應用程序已關閉。", "blue")
    except Exception as e:
        print_color(f"[錯誤] {e}", "red")
    
    # 詢問是否重新啟動
    while True:
        choice = input("\n您要退出嗎？(Y/N): ").strip().upper()
        if choice == "Y":
            break
        elif choice == "N":
            print("\n重新啟動應用...\n")
            launch_app()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print_color("\n應用程序已關閉。", "blue")
        else:
            print("請輸入Y或N")
    
    print_color("感謝使用PDF工具箱！", "green")
    input("按Enter鍵退出...")

if __name__ == "__main__":
    main() 