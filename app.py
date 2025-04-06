import streamlit as st
from streamlit_option_menu import option_menu
import os
import base64
from io import BytesIO

# 嘗試添加模組路徑
import sys
sys.path.append(os.path.abspath('.'))

# 檢查URL參數，啟用診斷模式
if "debug" in st.query_params:
    import subprocess
    import platform
    
    st.title("PDF工具箱系統診斷")
    
    # 系統信息
    st.header("系統信息")
    st.code(f"操作系統: {platform.system()} {platform.version()}")
    st.code(f"Python版本: {sys.version}")
    st.code(f"工作目錄: {os.getcwd()}")
    st.code(f"PATH環境變量: {os.environ.get('PATH', '未設置')}")
    
    # 檢查Ghostscript
    gs_path_found = False
    st.header("Ghostscript檢測")
    
    # 嘗試運行gs命令
    try:
        result = subprocess.run(["gs", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            st.success(f"Ghostscript版本: {result.stdout.strip()}")
            gs_path_found = True
        else:
            st.error(f"Ghostscript測試失敗: {result.stderr}")
    except Exception as e:
        st.error(f"執行gs命令出錯: {str(e)}")
    
    # 查找可能的gs路徑
    if not gs_path_found:
        st.write("搜索可能的Ghostscript路徑...")
        try:
            find_cmd = "find /usr -name gs -type f 2>/dev/null | head -5"
            result = subprocess.run(find_cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                st.code(f"找到以下可能的Ghostscript路徑:\n{result.stdout}")
            else:
                st.warning("未找到gs執行檔")
                
            # 嘗試其他可能的位置
            alt_paths = [
                "/usr/bin/gs",
                "/usr/local/bin/gs",
                "/bin/gs"
            ]
            
            for path in alt_paths:
                if os.path.exists(path):
                    st.success(f"找到Ghostscript在: {path}")
                    # 測試這個路徑
                    try:
                        result = subprocess.run([path, "--version"], capture_output=True, text=True)
                        if result.returncode == 0:
                            st.success(f"路徑 {path} 的Ghostscript版本: {result.stdout.strip()}")
                            gs_path_found = True
                    except Exception as e:
                        st.error(f"測試 {path} 時出錯: {str(e)}")
        except Exception as e:
            st.error(f"搜索Ghostscript路徑出錯: {str(e)}")
    
    # 檢查Poppler
    st.header("Poppler檢測")
    pdftoppm_found = False
    
    try:
        result = subprocess.run(["which", "pdftoppm"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pdftoppm_path = result.stdout.strip()
            st.success(f"找到Poppler (pdftoppm) 在: {pdftoppm_path}")
            pdftoppm_found = True
            
            # 檢查版本
            ver_result = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True)
            if ver_result.stderr:  # pdftoppm通常將版本信息輸出到stderr
                st.success(f"Poppler版本: {ver_result.stderr.strip()}")
    except Exception as e:
        st.error(f"檢查pdftoppm時出錯: {str(e)}")
    
    if not pdftoppm_found:
        st.write("搜索可能的Poppler (pdftoppm) 路徑...")
        try:
            find_cmd = "find /usr -name pdftoppm -type f 2>/dev/null | head -5"
            result = subprocess.run(find_cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                st.code(f"找到以下可能的pdftoppm路徑:\n{result.stdout}")
        except Exception as e:
            st.error(f"搜索pdftoppm路徑出錯: {str(e)}")
    
    # 測試指令
    st.header("命令執行測試")
    
    # 測試Ghostscript基本功能
    if gs_path_found:
        st.subheader("Ghostscript基本功能測試")
        try:
            test_cmd = "gs -dNOPAUSE -dBATCH -sDEVICE=nullpage -c quit"
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                st.success("Ghostscript基本功能測試成功")
            else:
                st.error(f"Ghostscript功能測試失敗: {result.stderr}")
        except Exception as e:
            st.error(f"執行Ghostscript測試命令出錯: {str(e)}")
    
    # 測試Poppler基本功能
    if pdftoppm_found:
        st.subheader("Poppler基本功能測試")
        st.code("Poppler已安裝並可用")
        
    # 命令執行工具
    st.header("命令執行工具")
    cmd = st.text_input("輸入要執行的命令")
    if st.button("執行"):
        if cmd:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                st.code(f"退出碼: {result.returncode}")
                if result.stdout:
                    st.subheader("標準輸出")
                    st.code(result.stdout)
                if result.stderr:
                    st.subheader("標準錯誤")
                    st.code(result.stderr)
            except Exception as e:
                st.error(f"執行命令時出錯: {str(e)}")
    
    # 退出診斷模式
    st.info("診斷完成。要回到主應用，請移除URL中的'?debug=1'參數。")
    st.stop()

# 引入功能模塊
try:
    from modules.merge import pdf_merge_page
    from modules.split import pdf_split_page
    from modules.rotate import pdf_rotate_page
    from modules.compress import pdf_compress_page
    from modules.extract_text import pdf_extract_text_page
    from modules.convert_to_image import pdf_to_image_page
    from modules.encrypt_decrypt import pdf_encrypt_decrypt_page
    from modules.metadata import pdf_metadata_page
    from modules.watermark import pdf_watermark_page
    from modules.optimize import pdf_optimize_page
except ImportError as e:
    st.error(f"模組導入錯誤: {str(e)}")
    st.stop()

# 頁面配置
st.set_page_config(
    page_title="PDF工具箱 | 多功能PDF處理工具",
    page_icon="🧰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f7ff;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #2563EB;
    }
    .sidebar .sidebar-content {
        background-color: #E0E7FF;
    }
    .download-button {
        background-color: #1E3A8A;
        color: white;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 5px;
        display: inline-block;
        margin-top: 1rem;
        font-weight: bold;
    }
    .download-button:hover {
        background-color: #2563EB;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def app():
    # 頁面標題
    st.title("🧰 PDF工具箱")
    st.subheader("您的多功能PDF處理中心")

    # 側邊欄菜單
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=100)
        st.title("PDF工具箱功能")
        
        selected = option_menu(
            menu_title=None,
            options=[
                "PDF合併", "PDF分割", "PDF旋轉", "PDF壓縮與優化", 
                "文字提取", "轉換為圖片", "加密/解密", 
                "編輯元數據", "添加水印", "舊版壓縮"
            ],
            icons=[
                "file-earmark-plus", "scissors", "arrow-clockwise", "file-zip", 
                "file-text", "file-image", "lock", 
                "pencil-square", "droplet", "gear"
            ],
            menu_icon="cast",
            default_index=0,
        )
        
        st.info("選擇上方的功能開始處理您的PDF文件。")
        
        # 頁腳
        st.markdown("---")
        st.caption("© 2025 PDF工具箱 | 版本 0.2")

    # 定義一個臨時函數
    def show_not_implemented(feature_name):
        st.header(f"{feature_name}")
        st.warning(f"{feature_name}功能尚未實現或正在加載中...")
        st.info("請先嘗試其他功能，或者聯繫開發者獲取更多信息。")

    # 主要內容區域 - 根據選擇顯示不同功能
    try:
        if selected == "PDF合併":
            pdf_merge_page()
        elif selected == "PDF分割":
            pdf_split_page()
        elif selected == "PDF旋轉":
            pdf_rotate_page()
        elif selected == "PDF壓縮與優化":
            pdf_compress_page()  # 將使用整合後的壓縮與優化功能
        elif selected == "文字提取":
            pdf_extract_text_page()
        elif selected == "轉換為圖片":
            pdf_to_image_page()
        elif selected == "加密/解密":
            pdf_encrypt_decrypt_page()
        elif selected == "編輯元數據":
            pdf_metadata_page()
        elif selected == "添加水印":
            pdf_watermark_page()
        elif selected == "舊版壓縮":
            from modules.legacy_compress import legacy_compress_page
            legacy_compress_page()
    except Exception as e:
        st.error(f"加載功能時出錯: {str(e)}")
        show_not_implemented(selected)

# 通用下載按鈕函數
def get_binary_file_downloader_html(bin_file, file_label='File', button_label='Download'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}" class="download-button">{button_label}</a>'
    return href

# 通用文件保存函數
def save_uploaded_file(uploaded_file, save_path):
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return save_path

def main():
    app()

if __name__ == "__main__":
    main() 