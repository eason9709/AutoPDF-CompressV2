import streamlit as st
import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

st.title("依賴檢測工具")

st.markdown("### 系統信息")
st.code(f"操作系統: {sys.platform}")
st.code(f"Python版本: {sys.version}")
st.code(f"工作目錄: {os.getcwd()}")

st.markdown("### 環境變量")
st.code(f"PATH: {os.environ.get('PATH', '未設置')}")

st.markdown("### Ghostscript 檢測")
gs_success, gs_path, _ = run_command("which gs")
if gs_success:
    st.success(f"在PATH中找到Ghostscript: {gs_path}")
    
    # 檢查版本
    gs_ver_success, gs_ver, _ = run_command("gs --version")
    if gs_ver_success:
        st.success(f"Ghostscript版本: {gs_ver}")
    else:
        st.warning("無法獲取Ghostscript版本")
else:
    st.error("在PATH中未找到Ghostscript")
    
    # 尋找可能的替代位置
    possible_gs_paths = [
        "/usr/bin/gs",
        "/usr/local/bin/gs",
        "/opt/homebrew/bin/gs",
        "/bin/gs"
    ]
    
    for path in possible_gs_paths:
        if os.path.exists(path):
            st.info(f"在替代位置找到Ghostscript: {path}")
            
            # 檢查版本
            gs_ver_success, gs_ver, _ = run_command(f"{path} --version")
            if gs_ver_success:
                st.info(f"Ghostscript版本: {gs_ver}")

st.markdown("### Poppler 檢測")
pdftoppm_success, pdftoppm_path, _ = run_command("which pdftoppm")
if pdftoppm_success:
    st.success(f"在PATH中找到Poppler (pdftoppm): {pdftoppm_path}")
    
    # 檢查版本
    pdftoppm_ver_success, pdftoppm_ver, _ = run_command("pdftoppm -v")
    if pdftoppm_ver_success:
        st.success(f"Poppler版本: {pdftoppm_ver}")
    else:
        st.warning("無法獲取Poppler版本")
else:
    st.error("在PATH中未找到Poppler (pdftoppm)")
    
    # 尋找可能的替代位置
    possible_pdftoppm_paths = [
        "/usr/bin/pdftoppm",
        "/usr/local/bin/pdftoppm",
        "/opt/homebrew/bin/pdftoppm",
        "/bin/pdftoppm",
        "/usr/lib/poppler/pdftoppm"
    ]
    
    for path in possible_pdftoppm_paths:
        if os.path.exists(path):
            st.info(f"在替代位置找到Poppler (pdftoppm): {path}")
            
            # 檢查版本
            pdftoppm_ver_success, pdftoppm_ver, _ = run_command(f"{path} -v")
            if pdftoppm_ver_success:
                st.info(f"Poppler版本: {pdftoppm_ver}")

st.markdown("### 搜索系統中的二進制文件")
find_gs_success, find_gs, _ = run_command("find / -name gs 2>/dev/null")
st.code(f"系統中的gs二進制文件:\n{find_gs}")

find_pdftoppm_success, find_pdftoppm, _ = run_command("find / -name pdftoppm 2>/dev/null")
st.code(f"系統中的pdftoppm二進制文件:\n{find_pdftoppm}")

st.markdown("### 為什麼pdf2image無法找到Poppler?")
st.markdown("""
pdf2image通常會在以下位置尋找Poppler:
1. 系統PATH
2. 環境變量中定義的路徑
3. 常見的安裝位置

可能的解決方案:
1. 在代碼中明確指定Poppler的路徑
2. 檢查Poppler是否正確安裝並添加到PATH
3. 設置環境變量
""")

# 顯示pdf2image如何使用poppler_path
import inspect
try:
    from pdf2image import convert_from_path
    st.code(inspect.getsource(convert_from_path), language="python")
except ImportError:
    st.error("無法導入pdf2image") 