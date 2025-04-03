#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF工具箱啟動腳本 - 用於安裝依賴項並啟動應用程序
包含解決網絡連接問題的增強參數
"""

import os
import sys
import subprocess
import platform
import time
import webbrowser  # 添加webbrowser模塊引入
import socket  # 添加socket模塊用於獲取網絡信息

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
            print_color("      推薦安裝方式:", "yellow")
            print_color("      1. 從 https://github.com/oschwartz10612/poppler-windows/releases/ 下載預編譯版本", "yellow")
            print_color("      2. 解壓到指定目錄（如C:\\Program Files\\poppler）", "yellow")
            print_color("      3. 將bin目錄添加到系統PATH環境變數", "yellow")
            print_color("\n      也可以使用官方最新版本(25.04)：", "cyan")
            print_color("      1. 從 https://poppler.freedesktop.org/ 下載tar.xz格式", "cyan")
            print_color("      2. 需使用7-Zip等工具解壓，並手動編譯（需要開發環境）", "cyan")
            print_color("      3. 初學者建議使用預編譯版本，更簡便", "cyan")
        elif platform.system() == "Darwin":  # macOS
            print_color("      運行: brew install poppler", "yellow")
            print_color("      或下載官方25.04版本: https://poppler.freedesktop.org/", "cyan")
        else:  # Linux
            print_color("      運行: sudo apt install poppler-utils", "yellow")
            print_color("      或下載官方25.04版本: https://poppler.freedesktop.org/", "cyan")
            print_color("      使用官方版本: tar -xf poppler-25.04.tar.xz && cd poppler-25.04 && ./configure && make && sudo make install", "cyan")
        
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
    
    # 檢查是否已安裝所需套件
    first_install = False
    try:
        import streamlit
    except ImportError:
        first_install = True
    
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
    
    # 如果是首次安裝，提示用戶可能需要重啟腳本
    if first_install:
        print_color("\n[重要提示] 由於這是首次安裝依賴，應用程序可能無法立即啟動", "yellow")
        print_color("如果遇到錯誤，請關閉此窗口並重新運行 'python run_toolkit.py'", "yellow")
        print_color("在某些系統上，需要重新啟動腳本才能正確載入新安裝的庫\n", "yellow")
        time.sleep(3)  # 暫停幾秒確保用戶看到提示
        
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
    
    # 確保在啟動前沒有正在運行的streamlit進程
    # 這些代碼已經移到kill_streamlit_processes函數中
    
    try:
        # 嘗試導入streamlit以確保已安裝
        import streamlit
        
        # 設置環境變數以確保自動打開瀏覽器
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "false"
        os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        
        # 啟動應用，使用顯式的server.headless=false參數
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            "app.py", 
            "--server.headless=false", 
            "--server.port=8501",
            "--server.address=0.0.0.0",         # 允許從任何地址訪問
            "--server.enableCORS=false",        # 禁用CORS限制
            "--server.enableXsrfProtection=false" # 禁用XSRF保護
        ]
        
        # 如果是Windows，使用subprocess.Popen啟動，並設置creationflags以避免顯示命令窗口
        if platform.system() == "Windows":
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW  # 避免顯示命令窗口
            )
        else:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        
        # 給Streamlit更多時間啟動 (增加等待時間)
        time.sleep(5)
        
        # 嘗試直接打開瀏覽器 (只嘗試一次)
        try:
            print_color("嘗試打開瀏覽器...", "blue")
            webbrowser.open('http://localhost:8501')
        except Exception as e:
            print_color(f"無法自動打開瀏覽器: {e}", "yellow")
            print_color("請手動打開瀏覽器並訪問以下地址之一:", "yellow")
            print_color("1. http://localhost:8501", "cyan")
            print_color("2. http://127.0.0.1:8501", "cyan")
            
            # 嘗試獲取本機IP地址
            try:
                hostname = socket.gethostname()
                ip_addresses = socket.gethostbyname_ex(hostname)[2]
                for ip in ip_addresses:
                    if not ip.startswith("127."):  # 排除localhost地址
                        print_color(f"3. http://{ip}:8501", "cyan")
            except:
                pass
        
        # 如果沒有出錯，返回True
        return True
        
    except ImportError:
        print_color("[錯誤] 未安裝streamlit，請重新運行安裝腳本", "red")
        return False
    except Exception as e:
        print_color(f"[錯誤] 啟動應用時出錯: {e}", "red")
        return False

def kill_streamlit_processes():
    """終止所有與streamlit相關的進程"""
    try:
        if platform.system() == "Windows":
            print_color("正在清理Streamlit進程...", "blue")
            # 終止streamlit.exe進程
            run_command("taskkill /f /im streamlit.exe >nul 2>&1", True)
            # 使用更安全的方式尋找並終止Python中運行的streamlit進程
            run_command('wmic process where "commandline like \'%streamlit%\'" call terminate >nul 2>&1', True)
            # 釋放8501端口
            run_command('netstat -ano | find ":8501" > temp_port.txt', True)
            if os.path.exists("temp_port.txt"):
                with open("temp_port.txt", "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            pid = parts[4]
                            run_command(f"taskkill /f /pid {pid} >nul 2>&1", True)
                os.remove("temp_port.txt")
        else:
            # Unix系統的進程清理
            run_command("pkill -f streamlit", True)
            run_command("lsof -ti:8501 | xargs kill -9 2>/dev/null", True)
    except Exception as e:
        print_color(f"清理進程時出錯: {e}", "yellow")
        
    # 等待確保進程已終止
    time.sleep(2)

def main():
    """主函數"""
    # 在啟動前清理可能存在的streamlit進程
    kill_streamlit_processes()
    
    # 首次執行提示
    print_color("第一次執行本啟動器可能需要安裝多個依賴項", "cyan")
    print_color("如果在安裝後遇到錯誤，請關閉並重新運行此腳本", "cyan")
    print_color("部分系統需要重新啟動腳本才能正確載入新安裝的庫\n", "cyan")
    
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
            print_color("應用已啟動！正確關閉方式: 按Ctrl+C或關閉瀏覽器後返回此窗口", "green")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print_color("\n應用程序已關閉。", "blue")
                # 確保清理所有相關進程
                kill_streamlit_processes()
    except Exception as e:
        print_color(f"[錯誤] {e}", "red")
        print_color("如果是首次安裝依賴，請關閉並重新運行此腳本", "yellow")
    
    # 詢問是否重新啟動
    while True:
        choice = input("\n您要退出嗎？(Y/N): ").strip().upper()
        if choice == "Y":
            break
        elif choice == "N":
            # 在重新啟動前先清理進程
            kill_streamlit_processes()
            print("\n重新啟動應用...\n")
            # 重啟但不再嘗試打開瀏覽器，避免多個瀏覽器窗口
            print_color("應用將在原瀏覽器窗口重新加載，請勿關閉現有瀏覽器窗口", "yellow")
            
            # 修改啟動命令，不自動打開瀏覽器
            cmd = [
                sys.executable, 
                "-m", 
                "streamlit", 
                "run", 
                "app.py", 
                "--server.headless=true",  # 不自動打開瀏覽器 
                "--server.port=8501",
                "--server.address=0.0.0.0",
                "--server.enableCORS=false",
                "--server.enableXsrfProtection=false"
            ]
            
            # 啟動但不打開新瀏覽器
            if platform.system() == "Windows":
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            print_color("應用已重新啟動！請刷新瀏覽器窗口", "green")
            print_color("正確關閉方式: 按Ctrl+C或關閉瀏覽器後返回此窗口", "green")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print_color("\n應用程序已關閉。", "blue")
                # 確保清理所有相關進程
                kill_streamlit_processes()
        else:
            print("請輸入Y或N")
    
    # 退出前確保所有streamlit進程已終止
    kill_streamlit_processes()
    print_color("感謝使用PDF工具箱！", "green")
    input("按Enter鍵退出...")

if __name__ == "__main__":
    main() 