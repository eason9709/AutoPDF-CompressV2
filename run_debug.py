#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF工具箱診斷腳本 - 用於解決連接和啟動問題
此腳本會詳細診斷Streamlit啟動問題並嘗試多種方法連接
"""

import os
import sys
import subprocess
import platform
import time
import socket
import webbrowser
from datetime import datetime

# 設置控制台為UTF-8編碼
if platform.system() == "Windows":
    os.system("chcp 65001 > nul")

print("=" * 60)
print("      PDF工具箱診斷工具 v1.0")
print("      用於解決連接和啟動問題")
print("=" * 60)
print()

# 獲取當前時間作為診斷ID
DIAGNOSTIC_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"diagnostic_{DIAGNOSTIC_ID}.log"

def log(message, to_console=True, level="INFO"):
    """記錄診斷信息到日誌文件和控制台"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level}] {message}"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")
    
    if to_console:
        print_color(message, "white" if level == "INFO" else 
                     "red" if level == "ERROR" else 
                     "yellow" if level == "WARNING" else 
                     "green" if level == "SUCCESS" else "cyan")

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
    log(f"執行命令: {command}", to_console=False)
    try:
        if silent:
            result = subprocess.run(
                command, shell=True, check=False,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        else:
            result = subprocess.run(command, shell=True, check=False, text=True)
        
        log(f"命令結果: 返回碼={result.returncode}, 輸出={result.stdout if silent else '直接輸出到控制台'}", to_console=False)
        return result.returncode == 0, result.stdout if silent else ""
    except Exception as e:
        log(f"執行命令時出錯: {e}", level="ERROR")
        return False, str(e)

def collect_system_info():
    """收集系統信息用於診斷"""
    log("開始收集系統診斷信息...", level="INFO")
    
    # 系統基本信息
    system_info = {
        "操作系統": platform.system(),
        "版本": platform.version(),
        "Python版本": sys.version,
        "本機名稱": socket.gethostname(),
    }
    
    for key, value in system_info.items():
        log(f"{key}: {value}")
    
    # 獲取IP地址
    try:
        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        log(f"IP地址: {', '.join(ip_addresses)}")
    except Exception as e:
        log(f"無法獲取IP地址: {e}", level="WARNING")
    
    # 檢查Python路徑
    log(f"Python路徑: {sys.executable}")
    
    # 檢查streamlit是否已安裝
    try:
        import streamlit
        log(f"Streamlit已安裝，版本: {streamlit.__version__}", level="SUCCESS")
    except ImportError:
        log("Streamlit未安裝", level="ERROR")
    except Exception as e:
        log(f"檢查Streamlit時出錯: {e}", level="ERROR")
    
    # 檢查其他依賴
    dependencies = ["PyPDF2", "pikepdf", "pillow", "reportlab", "pdf2image"]
    for dep in dependencies:
        try:
            __import__(dep.lower())
            log(f"{dep}已安裝", level="SUCCESS")
        except ImportError:
            log(f"{dep}未安裝", level="WARNING")
        except Exception as e:
            log(f"檢查{dep}時出錯: {e}", level="ERROR")
    
    # 檢查端口佔用情況
    check_port_usage()
    
    # 檢查app.py是否存在
    if os.path.exists("app.py"):
        log("找到app.py文件", level="SUCCESS")
    else:
        log("找不到app.py文件", level="ERROR")
    
    # 檢查防火牆狀態
    if platform.system() == "Windows":
        _, firewall_status = run_command("netsh advfirewall show allprofiles state", True)
        log(f"防火牆狀態:\n{firewall_status}", to_console=False)
        
        if "ON" in firewall_status:
            log("Windows防火牆已啟用，可能會阻止連接", level="WARNING")
    
    log("系統診斷信息收集完成", level="INFO")
    print()

def check_port_usage():
    """檢查關鍵端口使用情況"""
    log("檢查端口使用情況...", level="INFO")
    
    ports_to_check = [8501, 8502, 8503, 3000]
    
    for port in ports_to_check:
        if platform.system() == "Windows":
            _, port_result = run_command(f"netstat -ano | find \":{port}\"", True)
            if port_result.strip():
                log(f"端口{port}已被佔用:\n{port_result}", level="WARNING")
                # 嘗試獲取佔用進程的信息
                for line in port_result.strip().split('\n'):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        _, process_info = run_command(f"tasklist /fi \"PID eq {pid}\"", True)
                        log(f"佔用端口{port}的進程(PID {pid}):\n{process_info}", to_console=False)
            else:
                log(f"端口{port}未被佔用", level="SUCCESS")
        else:
            # Linux/Mac
            _, port_result = run_command(f"lsof -i:{port}", True)
            if port_result.strip():
                log(f"端口{port}已被佔用:\n{port_result}", level="WARNING")
            else:
                log(f"端口{port}未被佔用", level="SUCCESS")

def kill_streamlit_processes():
    """終止所有與streamlit相關的進程"""
    log("開始清理Streamlit相關進程...", level="INFO")
    
    success = False
    
    try:
        if platform.system() == "Windows":
            # 終止streamlit.exe進程
            ok1, res1 = run_command("taskkill /f /im streamlit.exe >nul 2>&1", True)
            log(f"終止streamlit.exe進程: {'成功' if ok1 else '失敗或無進程'}", level="INFO" if ok1 else "WARNING")
            
            # 使用更安全的方式尋找並終止Python中運行的streamlit進程
            ok2, res2 = run_command('wmic process where "commandline like \'%streamlit%\'" call terminate >nul 2>&1', True)
            log(f"終止Python中的streamlit進程: {'成功' if ok2 else '失敗或無進程'}", level="INFO" if ok2 else "WARNING")
            
            # 釋放8501端口
            _, port_info = run_command('netstat -ano | find ":8501"', True)
            if port_info.strip():
                log(f"發現佔用8501端口的進程:\n{port_info}", level="WARNING")
                
                for line in port_info.strip().split('\n'):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        ok3, _ = run_command(f"taskkill /f /pid {pid}", True)
                        log(f"終止PID {pid}: {'成功' if ok3 else '失敗'}", level="INFO" if ok3 else "ERROR")
                        success = success or ok3
            else:
                log("未發現佔用8501端口的進程", level="SUCCESS")
                success = True
        else:
            # Unix系統的進程清理
            ok1, _ = run_command("pkill -f streamlit", True)
            log(f"終止streamlit進程: {'成功' if ok1 else '失敗或無進程'}", level="INFO" if ok1 else "WARNING")
            
            ok2, _ = run_command("lsof -ti:8501 | xargs kill -9 2>/dev/null", True)
            log(f"釋放8501端口: {'成功' if ok2 else '失敗或無進程'}", level="INFO" if ok2 else "WARNING")
            
            success = ok1 or ok2
    except Exception as e:
        log(f"清理進程時出錯: {e}", level="ERROR")
    
    if success:
        log("進程清理完成", level="SUCCESS")
    else:
        log("進程清理過程中可能有問題，請見上方日誌", level="WARNING")
    
    # 等待確保進程已終止
    time.sleep(2)
    return success

def check_streamlit_installation():
    """詳細檢查streamlit安裝並嘗試修復"""
    log("檢查Streamlit安裝...", level="INFO")
    
    try:
        # 檢查streamlit安裝
        import streamlit
        streamlit_version = streamlit.__version__
        log(f"Streamlit已安裝，版本: {streamlit_version}", level="SUCCESS")
        
        # 檢查streamlit命令行是否可用
        _, streamlit_cmd_result = run_command(f"{sys.executable} -m streamlit --version", True)
        if streamlit_cmd_result.strip():
            log(f"Streamlit命令行工具可用: {streamlit_cmd_result.strip()}", level="SUCCESS")
            return True
        else:
            log("Streamlit命令行工具無法啟動，嘗試重新安裝...", level="WARNING")
    except ImportError:
        log("Streamlit未安裝，嘗試安裝...", level="WARNING")
    except Exception as e:
        log(f"檢查Streamlit時出錯: {e}", level="ERROR")
    
    # 嘗試重新安裝streamlit
    log("正在重新安裝Streamlit...", level="INFO")
    
    # 先卸載
    uninstall_ok, _ = run_command(f"{sys.executable} -m pip uninstall -y streamlit", True)
    if uninstall_ok:
        log("已卸載現有Streamlit", level="SUCCESS")
    
    # 安裝最新版本
    install_ok, install_result = run_command(f"{sys.executable} -m pip install streamlit", True)
    
    if install_ok:
        log("Streamlit重新安裝成功", level="SUCCESS")
        return True
    else:
        log(f"Streamlit安裝失敗:\n{install_result}", level="ERROR")
        return False

def try_direct_streamlit_run():
    """直接使用streamlit命令運行應用，用於捕獲錯誤信息"""
    log("嘗試直接使用streamlit命令運行應用以查看詳細錯誤...", level="INFO")
    
    if not os.path.exists("app.py"):
        log("找不到app.py文件，無法啟動應用", level="ERROR")
        return False, "找不到app.py文件"
    
    try:
        # 使用完整參數直接運行streamlit，捕獲所有輸出
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless=false",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false"
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10  # 10秒超時
        )
        
        if process.returncode == 0:
            log("直接運行Streamlit成功", level="SUCCESS")
            return True, "正常啟動"
        else:
            error_output = process.stderr
            log(f"直接運行Streamlit失敗，錯誤輸出:\n{error_output}", level="ERROR")
            return False, error_output
    except subprocess.TimeoutExpired:
        log("直接運行Streamlit超時，可能是正常啟動中", level="WARNING")
        return True, "啟動中（超時）"
    except Exception as e:
        log(f"嘗試直接運行Streamlit時出錯: {e}", level="ERROR")
        return False, str(e)

def launch_diagnostic():
    """診斷版啟動函數，嘗試多種方法啟動Streamlit"""
    log("\n===== 啟動診斷模式 =====", level="INFO")
    
    # 先嘗試直接運行以獲取錯誤信息
    direct_ok, direct_result = try_direct_streamlit_run()
    
    # 嘗試使用不同端口啟動
    ports_to_try = [8501, 8502, 8503, 3000]
    success = False
    used_port = 8501
    
    for port in ports_to_try:
        log(f"嘗試使用端口 {port}...", level="INFO")
        
        # 確保端口沒有被佔用
        if platform.system() == "Windows":
            _, port_check = run_command(f"netstat -ano | find \":{port}\"", True)
            if port_check.strip():
                log(f"端口{port}已被佔用，嘗試釋放...", level="WARNING")
                
                for line in port_check.strip().split('\n'):
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        run_command(f"taskkill /f /pid {pid}", True)
        else:
            # Linux/Mac
            run_command(f"lsof -ti:{port} | xargs kill -9 2>/dev/null", True)
        
        # 等待端口釋放
        time.sleep(1)
        
        # 構建啟動命令
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            "app.py", 
            "--server.headless=false", 
            f"--server.port={port}",
            "--server.address=0.0.0.0",  # 允許從任何地址訪問
            "--server.enableCORS=false",  # 禁用CORS限制
            "--server.enableXsrfProtection=false",  # 禁用XSRF保護
            "--browser.serverAddress=localhost"
        ]
        
        try:
            # 使用Popen啟動進程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            )
            
            # 等待檢查啟動狀態
            time.sleep(5)
            
            # 檢查進程是否仍在運行
            if process.poll() is None:  # None表示進程仍在運行
                log(f"Streamlit已在端口{port}啟動", level="SUCCESS")
                success = True
                used_port = port
                break
            else:
                # 進程已終止，獲取錯誤輸出
                stdout, stderr = process.communicate()
                log(f"Streamlit啟動失敗。錯誤:\n{stderr}", level="ERROR")
        except Exception as e:
            log(f"嘗試啟動端口{port}時出錯: {str(e)}", level="ERROR")
    
    # 最終結果處理
    if success:
        log_final_success_info(used_port)
        return True
    else:
        log_diagnostic_failure()
        return False

def log_final_success_info(port):
    """顯示成功啟動後的診斷信息和訪問方式"""
    log("\n[成功] Streamlit已啟動", level="SUCCESS")
    
    # 獲取所有可能的訪問地址
    log("請嘗試使用以下地址訪問:", level="INFO")
    log(f"1. http://localhost:{port}", level="SUCCESS")
    log(f"2. http://127.0.0.1:{port}", level="SUCCESS")
    
    # 獲取本機IP地址
    try:
        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        
        for i, ip in enumerate(ip_addresses, 3):
            if not ip.startswith("127."):  # 排除localhost地址
                log(f"{i}. http://{ip}:{port}", level="SUCCESS")
    except Exception as e:
        log(f"無法獲取本機IP地址: {e}", level="WARNING")
    
    # 嘗試自動打開瀏覽器
    log("嘗試自動打開瀏覽器...", level="INFO")
    try:
        webbrowser.open(f'http://localhost:{port}')
        log("瀏覽器已自動打開", level="SUCCESS")
    except Exception as e:
        log(f"無法自動打開瀏覽器: {e}", level="WARNING")
        log("請手動打開瀏覽器並訪問上述地址", level="INFO")
    
    log("\n診斷日誌已保存到: " + os.path.abspath(LOG_FILE), level="INFO")
    log("如果仍然無法連接，請嘗試使用完整診斷報告中的建議", level="INFO")

def log_diagnostic_failure():
    """顯示啟動失敗的診斷信息和可能的解決方案"""
    log("\n[失敗] 所有啟動嘗試均未成功", level="ERROR")
    
    log("\n可能的原因:", level="WARNING")
    log("1. Streamlit庫安裝不完整或損壞", level="WARNING")
    log("2. 網絡配置問題阻止了連接", level="WARNING")
    log("3. Python環境問題或缺少依賴", level="WARNING")
    log("4. 防火牆或安全軟件阻止", level="WARNING")
    log("5. 端口8501被其他應用佔用", level="WARNING")
    
    log("\n建議解決方案:", level="INFO")
    log("1. 重新安裝Streamlit: pip uninstall streamlit && pip install streamlit", level="INFO")
    log("2. 臨時關閉防火牆或安全軟件測試", level="INFO")
    log("3. 嘗試以管理員身份運行此腳本", level="INFO")
    log("4. 檢查網絡設置，特別是防火牆和代理配置", level="INFO")
    log("5. 手動終止佔用端口的進程後重試", level="INFO")
    log("6. 在命令提示符中直接運行: python -m streamlit run app.py", level="INFO")
    
    log("\n診斷日誌已保存到: " + os.path.abspath(LOG_FILE), level="INFO")
    log("請將此日誌文件提供給技術支持以獲取進一步幫助", level="INFO")

def main():
    """主函數"""
    try:
        # 刪除之前的診斷日誌
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        
        log("PDF工具箱診斷工具啟動", level="INFO")
        log(f"診斷ID: {DIAGNOSTIC_ID}", level="INFO")
        log(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", level="INFO")
        log(f"Python版本: {sys.version}", level="INFO")
        log(f"操作系統: {platform.system()} {platform.version()}", level="INFO")
        print()
        
        # 收集系統信息
        collect_system_info()
        
        # 終止現有Streamlit進程
        kill_streamlit_processes()
        
        # 檢查並修復Streamlit安裝
        check_streamlit_installation()
        
        # 嘗試啟動Streamlit
        app_launched = launch_diagnostic()
        
        # 等待用戶關閉
        if app_launched:
            try:
                while True:
                    print()
                    log("應用正在運行中。按Ctrl+C可終止應用", level="INFO")
                    time.sleep(5)
            except KeyboardInterrupt:
                log("\n用戶終止了應用", level="INFO")
                kill_streamlit_processes()
        
        log("診斷結束", level="INFO")
        log(f"診斷日誌: {os.path.abspath(LOG_FILE)}", level="INFO")
        print()
        
        input("按Enter鍵退出...")
    except Exception as e:
        log(f"診斷過程中出現未預期錯誤: {e}", level="ERROR")
        print()
        print(f"診斷日誌已保存到: {os.path.abspath(LOG_FILE)}")
        input("按Enter鍵退出...")

if __name__ == "__main__":
    main() 