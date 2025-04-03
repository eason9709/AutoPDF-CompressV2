import streamlit as st
from streamlit_option_menu import option_menu
import os
import base64
from io import BytesIO

# 嘗試添加模組路徑
import sys
sys.path.append(os.path.abspath('.'))

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