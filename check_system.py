import streamlit as st
import subprocess
import os
import platform
import sys
import glob

def run_command(cmd):
    """執行命令並返回結果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

st.title("PDF工具箱系統診斷工具")
st.write("這個工具用於檢查系統是否正確安裝了所需的依賴項。")

# 系統信息
st.header("系統信息")
st.code(f"操作系統: {platform.system()} {platform.version()}")
st.code(f"Python版本: {sys.version}")
st.code(f"工作目錄: {os.getcwd()}")
st.code(f"PATH環境變量: {os.environ.get('PATH', '未設置')}")

# Ghostscript 檢測
st.header("Ghostscript檢測")

# 根據不同操作系統檢查
gs_executable = "gs"
if platform.system() == "Windows":
    gs_executable = "gswin64c.exe"  # 64位Windows上的Ghostscript執行檔名稱
    gs_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'gs', '*', 'bin', gs_executable),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'gs', '*', 'bin', gs_executable)
    ]
    
    # 使用glob查找所有可能的Ghostscript路徑
    found_gs_paths = []
    for path_pattern in gs_paths:
        found_gs_paths.extend(glob.glob(path_pattern))
    
    for gs_path in found_gs_paths:
        st.success(f"找到Ghostscript: {gs_path}")
        gs_ver_success, gs_ver, _ = run_command(f'"{gs_path}" --version')
        if gs_ver_success:
            st.success(f"Ghostscript版本: {gs_ver}")

# 使用which命令或where命令
if platform.system() == "Windows":
    gs_which_success, gs_which_output, _ = run_command("where gs")
else:
    gs_which_success, gs_which_output, _ = run_command("which gs")

if gs_which_success:
    st.success(f"在PATH中找到Ghostscript: {gs_which_output}")
    gs_ver_success, gs_ver, _ = run_command("gs --version")
    if gs_ver_success:
        st.success(f"Ghostscript版本: {gs_ver}")
else:
    st.warning("在PATH中未找到Ghostscript")

# 測試Ghostscript功能
st.subheader("Ghostscript功能測試")
gs_test_cmd = "gs -dNOPAUSE -dBATCH -sDEVICE=nullpage -c quit"
gs_test_success, gs_test_out, gs_test_err = run_command(gs_test_cmd)
if gs_test_success:
    st.success("Ghostscript基本功能測試成功")
else:
    st.error(f"Ghostscript功能測試失敗: {gs_test_err}")

# Poppler 檢測
st.header("Poppler檢測")

# 根據不同操作系統檢查
pdftoppm_executable = "pdftoppm"
if platform.system() == "Windows":
    pdftoppm_executable += ".exe"
    poppler_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'poppler', 'bin', pdftoppm_executable),
        os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'poppler', 'bin', pdftoppm_executable),
        os.path.expanduser(f'~\\poppler\\bin\\{pdftoppm_executable}')
    ]
    
    for pdftoppm_path in poppler_paths:
        if os.path.exists(pdftoppm_path):
            st.success(f"找到Poppler (pdftoppm): {pdftoppm_path}")
            pdftoppm_ver_success, _, pdftoppm_ver = run_command(f'"{pdftoppm_path}" -v')
            if pdftoppm_ver:
                st.success(f"Poppler版本: {pdftoppm_ver}")

# 使用which命令或where命令
if platform.system() == "Windows":
    pdftoppm_which_success, pdftoppm_which_output, _ = run_command("where pdftoppm")
else:
    pdftoppm_which_success, pdftoppm_which_output, _ = run_command("which pdftoppm")

if pdftoppm_which_success:
    st.success(f"在PATH中找到Poppler (pdftoppm): {pdftoppm_which_output}")
    pdftoppm_ver_success, _, pdftoppm_ver = run_command("pdftoppm -v")
    if pdftoppm_ver:
        st.success(f"Poppler版本: {pdftoppm_ver}")
else:
    st.warning("在PATH中未找到Poppler (pdftoppm)")

# Linux系統上的附加檢查
if platform.system() != "Windows":
    poppler_find_cmd = "find /usr -name pdftoppm -type f 2>/dev/null | head -5"
    poppler_find_success, poppler_find_output, _ = run_command(poppler_find_cmd)
    if poppler_find_output:
        st.success(f"在系統中找到Poppler (pdftoppm):\n{poppler_find_output}")

# Python依賴檢測
st.header("Python依賴檢測")

# 檢查pdf2image
try:
    import pdf2image
    st.success(f"pdf2image版本: {pdf2image.__version__}")
    
    # 獲取pdf2image使用的Poppler路徑
    try:
        # 嘗試調用pdf2image的內部方法來檢查Poppler路徑
        from pdf2image.pdf2image import get_poppler_path
        poppler_path = get_poppler_path()
        if poppler_path:
            st.success(f"pdf2image使用的Poppler路徑: {poppler_path}")
        else:
            st.warning("pdf2image未找到Poppler路徑")
    except Exception as e:
        st.warning(f"無法獲取pdf2image的Poppler路徑: {e}")
except ImportError:
    st.error("未安裝pdf2image")

# 檢查PyPDF2
try:
    import PyPDF2
    st.success(f"PyPDF2版本: {PyPDF2.__version__}")
except ImportError:
    st.error("未安裝PyPDF2")

# 檢查pikepdf
try:
    import pikepdf
    st.success(f"pikepdf版本: {pikepdf.__version__}")
except ImportError:
    st.error("未安裝pikepdf")

# 嘗試創建測試PDF並使用Ghostscript
st.header("功能測試")

# 創建測試目錄
with st.expander("執行完整功能測試", expanded=False):
    import tempfile
    
    with tempfile.TemporaryDirectory() as temp_dir:
        st.write(f"創建臨時測試目錄: {temp_dir}")
        
        # 建立一個簡單的PDF
        test_pdf_path = os.path.join(temp_dir, "test.pdf")
        try:
            from reportlab.pdfgen import canvas
            
            st.write("創建測試PDF...")
            c = canvas.Canvas(test_pdf_path)
            c.drawString(100, 750, "測試PDF文檔")
            c.save()
            
            if os.path.exists(test_pdf_path):
                st.success(f"成功創建測試PDF: {test_pdf_path} ({os.path.getsize(test_pdf_path)} bytes)")
            
            # 測試Ghostscript壓縮
            if gs_which_success:
                compressed_pdf_path = os.path.join(temp_dir, "compressed.pdf")
                gs_cmd = f'gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH -sOutputFile="{compressed_pdf_path}" "{test_pdf_path}"'
                gs_compress_success, _, gs_compress_err = run_command(gs_cmd)
                
                if gs_compress_success and os.path.exists(compressed_pdf_path):
                    st.success(f"Ghostscript壓縮測試成功: {compressed_pdf_path} ({os.path.getsize(compressed_pdf_path)} bytes)")
                else:
                    st.error(f"Ghostscript壓縮測試失敗: {gs_compress_err}")
            
            # 測試pdf2image和Poppler
            if pdftoppm_which_success:
                try:
                    from pdf2image import convert_from_path
                    
                    st.write("測試pdf2image轉換PDF為圖像...")
                    images = convert_from_path(test_pdf_path)
                    
                    if images and len(images) > 0:
                        st.success(f"pdf2image轉換測試成功: 成功轉換 {len(images)} 頁")
                        
                        # 顯示第一頁圖像
                        st.image(images[0], caption="測試PDF的第一頁", width=300)
                    else:
                        st.error("pdf2image轉換測試失敗: 未產生圖像")
                except Exception as e:
                    st.error(f"pdf2image轉換測試失敗: {str(e)}")
        
        except Exception as e:
            st.error(f"功能測試出錯: {str(e)}")

# 命令執行工具
st.header("命令執行工具")
st.write("輸入系統命令來診斷問題（請謹慎使用）")

cmd = st.text_input("輸入要執行的命令")
if st.button("執行命令"):
    if cmd:
        success, stdout, stderr = run_command(cmd)
        st.code(f"Exit Code: {0 if success else 1}")
        if stdout:
            st.subheader("標準輸出")
            st.code(stdout)
        if stderr:
            st.subheader("標準錯誤")
            st.code(stderr)
    else:
        st.warning("請輸入要執行的命令")

# 診斷報告和建議
st.header("診斷報告和建議")

# 根據檢測結果提供建議
suggestions = []

if not gs_which_success:
    if platform.system() == "Windows":
        suggestions.append("- 安裝Ghostscript: 下載並安裝 [Ghostscript for Windows](https://ghostscript.com/releases/gsdnld.html)")
        suggestions.append("- 確保Ghostscript的bin目錄已添加到PATH環境變量中")
    elif platform.system() == "Darwin":  # macOS
        suggestions.append("- 使用Homebrew安裝Ghostscript: `brew install ghostscript`")
    else:  # Linux
        suggestions.append("- 使用apt安裝Ghostscript: `sudo apt-get install ghostscript`")

if not pdftoppm_which_success:
    if platform.system() == "Windows":
        suggestions.append("- 安裝Poppler: 下載 [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)")
        suggestions.append("- 解壓縮並確保Poppler的bin目錄已添加到PATH環境變量中")
    elif platform.system() == "Darwin":  # macOS
        suggestions.append("- 使用Homebrew安裝Poppler: `brew install poppler`")
    else:  # Linux
        suggestions.append("- 使用apt安裝Poppler: `sudo apt-get install poppler-utils`")

try:
    import pytesseract
except ImportError:
    suggestions.append("- 安裝pytesseract: `pip install pytesseract`")
    suggestions.append("- 安裝Tesseract OCR引擎並確保其在PATH中")

if suggestions:
    st.subheader("建議操作")
    for suggestion in suggestions:
        st.markdown(suggestion)
else:
    st.success("所有依賴項檢測正常！您的系統已經準備好運行PDF工具箱。")

# 在Streamlit Cloud環境下的特別說明
st.header("Streamlit Cloud部署注意事項")
st.markdown("""
### Streamlit Cloud部署

在Streamlit Cloud上部署時，需要在根目錄創建`packages.txt`文件，列出需要安裝的系統依賴項：

```
ghostscript
poppler-utils
```

這將使Streamlit Cloud自動安裝必要的系統依賴。
""")

# 顯示當前目錄下是否存在packages.txt
if os.path.exists("packages.txt"):
    with open("packages.txt", "r") as f:
        content = f.read()
    st.success("檢測到packages.txt文件:")
    st.code(content)
else:
    st.warning("未檢測到packages.txt文件。如需部署到Streamlit Cloud，請創建該文件。") 