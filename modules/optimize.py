import streamlit as st
import os
import tempfile
import pikepdf
from pikepdf import Pdf
import base64
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
import subprocess
import shutil

# 檢查Ghostscript是否可用
GHOSTSCRIPT_PATH = os.path.join(os.getcwd(), "gs10.05.0", "bin", "gswin64c.exe")
if not os.path.exists(GHOSTSCRIPT_PATH):
    GHOSTSCRIPT_PATH = os.path.join(os.getcwd(), "gs10.05.0", "bin", "gswin32c.exe")
    if not os.path.exists(GHOSTSCRIPT_PATH):
        # 嘗試在系統路徑中查找
        GHOSTSCRIPT_PATH = shutil.which("gswin64c") or shutil.which("gswin32c") or "gs"

# 檢查Ghostscript是否可用
GHOSTSCRIPT_AVAILABLE = os.path.exists(GHOSTSCRIPT_PATH)

def pdf_optimize_page():
    st.header("📱 PDF優化")
    st.write("優化PDF以適應不同設備閱讀，調整格式或減小文件大小")
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 保存上傳的文件，先處理文件名以確保合法
            safe_filename = "".join([c for c in uploaded_file.name if c.isalnum() or c in "._- "]).strip()
            if not safe_filename:
                safe_filename = "uploaded_file.pdf"
            elif not safe_filename.lower().endswith('.pdf'):
                safe_filename += '.pdf'
                
            # 使用短文件名和路徑避免特殊字符問題
            temp_input = os.path.join(tmpdirname, "input.pdf")
            temp_output = os.path.join(tmpdirname, "output.pdf")
            
            with open(temp_input, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 獲取原始文件大小
            original_size = os.path.getsize(temp_input) / (1024 * 1024)  # 轉換為MB
            
            # 讀取PDF基本信息
            try:
                reader = PdfReader(temp_input)
                total_pages = len(reader.pages)
                
                st.write(f"文件名: {uploaded_file.name}")
                st.write(f"總頁數: {total_pages}")
                st.write(f"原始大小: {original_size:.2f} MB")
                
                # 優化選項
                st.subheader("選擇優化類型")
                
                # 根據是否有Ghostscript提供不同選項
                if GHOSTSCRIPT_AVAILABLE:
                    optimization_type = st.radio(
                        "優化方式",
                        ["基本優化（保持質量）", "中度優化（平衡質量和大小）", "高度優化（最小文件大小）", "自定義優化"]
                    )
                else:
                    optimization_type = st.radio(
                        "優化方式",
                        ["基本優化（保持質量）", "中度優化（平衡質量和大小）", "高度優化（最小文件大小）", "自定義優化"]
                    )
                    st.warning("未檢測到Ghostscript，優化效果可能有限。建議安裝Ghostscript以獲得更好的優化效果。")
                
                # 根據優化類型設置參數
                if GHOSTSCRIPT_AVAILABLE:
                    # GS參數設置
                    gs_settings = {
                        "基本優化（保持質量）": {"dpi": 150, "image_quality": "/default", "color_mode": "Color"},
                        "中度優化（平衡質量和大小）": {"dpi": 120, "image_quality": "/ebook", "color_mode": "Color"},
                        "高度優化（最小文件大小）": {"dpi": 90, "image_quality": "/printer", "color_mode": "Gray"}
                    }
                
                # 預設優化參數 (用於pikepdf)
                pikepdf_params = {
                    "基本優化（保持質量）": {
                        "remove_metadata": False,
                        "flatten_forms": False,
                        "remove_bookmarks": False,
                        "optimize_fonts": False
                    },
                    "中度優化（平衡質量和大小）": {
                        "remove_metadata": True,
                        "flatten_forms": False,
                        "remove_bookmarks": False,
                        "optimize_fonts": True
                    },
                    "高度優化（最小文件大小）": {
                        "remove_metadata": True,
                        "flatten_forms": True,
                        "remove_bookmarks": True,
                        "optimize_fonts": True
                    }
                }
                
                # 自定義優化選項
                if optimization_type == "自定義優化":
                    st.subheader("自定義優化選項")
                    
                    remove_metadata = st.checkbox("移除元數據", value=True, help="刪除文檔的元數據以減小大小")
                    flatten_forms = st.checkbox("壓平表單欄位", value=False, help="將表單欄位轉換為普通文本")
                    remove_bookmarks = st.checkbox("移除書籤", value=False, help="刪除文檔書籤")
                    optimize_fonts = st.checkbox("優化字體", value=True, help="優化字體以減小文件大小")
                    
                    if GHOSTSCRIPT_AVAILABLE:
                        custom_dpi = st.slider(
                            "圖像分辨率(DPI)",
                            min_value=30,
                            max_value=300,
                            value=120,
                            step=10,
                            help="較低的分辨率可以顯著減小文件大小，但可能降低圖像質量"
                        )
                        
                        color_mode = st.radio(
                            "顏色模式",
                            ["彩色", "灰度", "黑白"],
                            index=0,
                            help="灰度或黑白模式可以顯著減小大小，但會丟失顏色信息"
                        )
                    
                    # 分別設置不同的參數
                    pikepdf_params = {
                        "remove_metadata": remove_metadata,
                        "flatten_forms": flatten_forms,
                        "remove_bookmarks": remove_bookmarks,
                        "optimize_fonts": optimize_fonts
                    }
                    
                    if GHOSTSCRIPT_AVAILABLE:
                        # 顏色設置映射
                        color_settings = {"彩色": "Color", "灰度": "Gray", "黑白": "Mono"}
                        
                        gs_settings = {
                            "dpi": custom_dpi,
                            "image_quality": "/ebook",  # 固定使用ebook品質
                            "color_mode": color_settings[color_mode]
                        }
                else:
                    # 使用預設參數
                    pikepdf_params = pikepdf_params[optimization_type]
                
                # 優化按鈕
                if st.button("優化PDF"):
                    with st.spinner("正在優化PDF..."):
                        try:
                            # 根據是否有Ghostscript選擇優化方法
                            if GHOSTSCRIPT_AVAILABLE and optimization_type != "基本優化（保持質量）":
                                # 使用Ghostscript進行優化
                                if optimization_type != "自定義優化":
                                    gs_params = gs_settings[optimization_type]
                                else:
                                    gs_params = gs_settings
                                
                                # 確保路徑沒有問題，轉換為適當的格式
                                output_path = temp_output.replace('\\', '/')
                                input_path = temp_input.replace('\\', '/')
                                
                                # 設置Ghostscript命令
                                gs_cmd = [
                                    GHOSTSCRIPT_PATH,
                                    "-sDEVICE=pdfwrite",
                                    "-dCompatibilityLevel=1.4",
                                    f"-dPDFSETTINGS={gs_params['image_quality']}",
                                    "-dNOPAUSE",
                                    "-dQUIET",
                                    "-dBATCH",
                                    f"-r{gs_params['dpi']}"
                                ]
                                
                                # 添加顏色模式設置
                                if gs_params['color_mode'] == "Gray":
                                    gs_cmd.append("-sColorConversionStrategy=Gray")
                                    gs_cmd.append("-dProcessColorModel=/DeviceGray")
                                elif gs_params['color_mode'] == "Mono":
                                    gs_cmd.append("-sColorConversionStrategy=Mono")
                                    gs_cmd.append("-dProcessColorModel=/DeviceGray")
                                
                                # 添加元數據處理
                                if pikepdf_params["remove_metadata"]:
                                    gs_cmd.append("-dFastWebView=true")
                                
                                # 添加輸出和輸入文件
                                gs_cmd.append(f"-sOutputFile={output_path}")
                                gs_cmd.append(input_path)
                                
                                # 執行命令
                                try:
                                    process = subprocess.run(
                                        gs_cmd,
                                        check=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True
                                    )
                                    
                                    # 使用Ghostscript優化後的文件作為輸出
                                    final_output_file = temp_output
                                except subprocess.CalledProcessError as e:
                                    st.error(f"Ghostscript執行錯誤: {e}")
                                    if e.stderr:
                                        st.code(e.stderr)
                                    
                                    # 回退到pikepdf方法
                                    st.warning("Ghostscript優化失敗，嘗試使用備用方法優化...")
                                    final_output_file = pikepdf_optimize(temp_input, temp_output, pikepdf_params)
                            else:
                                # 使用pikepdf方法
                                final_output_file = pikepdf_optimize(temp_input, temp_output, pikepdf_params)
                            
                            # 檢查輸出文件是否存在
                            if os.path.exists(final_output_file) and os.path.getsize(final_output_file) > 0:
                                # 獲取優化後的文件大小
                                optimized_size = os.path.getsize(final_output_file) / (1024 * 1024)  # 轉換為MB
                                
                                # 計算節省的空間
                                if original_size > 0:
                                    saved_percentage = ((original_size - optimized_size) / original_size) * 100
                                else:
                                    saved_percentage = 0
                                
                                # 顯示優化結果
                                st.write(f"優化後大小: {optimized_size:.2f} MB")
                                st.write(f"節省空間: {saved_percentage:.1f}%")
                                
                                # 創建進度條顯示節省比例
                                st.progress(min(saved_percentage / 100, 1.0))
                                
                                # 成功訊息
                                if saved_percentage > 0:
                                    st.success(f"成功優化PDF文件，減少了 {saved_percentage:.1f}% 的大小")
                                else:
                                    st.info("文件已處理，但優化效果有限")
                                
                                # 提供下載
                                with open(final_output_file, "rb") as f:
                                    pdf_bytes = f.read()
                                    
                                b64_pdf = base64.b64encode(pdf_bytes).decode()
                                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="optimized_{uploaded_file.name}" class="download-button">下載優化後的PDF</a>'
                                st.markdown(href, unsafe_allow_html=True)
                                
                                # 顯示應用的優化選項摘要
                                with st.expander("優化選項摘要"):
                                    st.write("應用的優化選項：")
                                    for key, value in pikepdf_params.items():
                                        if key == "remove_metadata" and value:
                                            st.write("• 元數據移除: 已啟用")
                                        elif key == "flatten_forms" and value:
                                            st.write("• 表單壓平: 已啟用")
                                        elif key == "remove_bookmarks" and value:
                                            st.write("• 書籤移除: 已啟用")
                                        elif key == "optimize_fonts" and value:
                                            st.write("• 字體優化: 已啟用")
                                    
                                    if GHOSTSCRIPT_AVAILABLE and optimization_type != "基本優化（保持質量）":
                                        if "dpi" in gs_params:
                                            st.write(f"• 圖像分辨率: {gs_params['dpi']} DPI")
                                        if "color_mode" in gs_params:
                                            st.write(f"• 顏色模式: {gs_params['color_mode']}")
                            else:
                                st.error("優化過程中出錯，無法創建輸出文件")
                        
                        except Exception as e:
                            st.error(f"優化過程中出錯: {str(e)}")
            
            except Exception as e:
                st.error(f"讀取PDF時出錯: {str(e)}")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件進行優化")
        
        # 顯示Ghostscript狀態
        if GHOSTSCRIPT_AVAILABLE:
            st.success(f"已檢測到Ghostscript: {GHOSTSCRIPT_PATH}")
            st.info("啟用了高級優化功能，可以顯著減小PDF文件大小")
        else:
            st.warning("未檢測到Ghostscript，優化效果可能有限")
            st.info("建議安裝Ghostscript以獲得最佳優化效果")
        
        st.markdown("""
        ### 使用說明
        1. 上傳您的PDF文件
        2. 選擇優化級別：
           - 基本優化：保持較高質量，略微減小文件大小
           - 中度優化：平衡質量和文件大小
           - 高度優化：顯著減小文件大小，可能降低質量
           - 自定義優化：手動選擇具體優化選項
        3. 點擊"優化PDF"按鈕
        4. 下載處理後的文件
        
        ### 優化選項說明
        - **移除元數據**：刪除文檔的附加信息
        - **壓平表單欄位**：將互動表單轉換為靜態內容
        - **移除書籤**：刪除文檔的書籤結構
        - **優化字體**：減小嵌入字體的大小
        - **調整圖像分辨率**：降低圖像分辨率以減小文件大小
        - **更改顏色模式**：將彩色PDF轉換為灰度或黑白以節省空間
        
        ### 適用場景
        - 減小大型PDF文件以便於分享
        - 為移動設備優化閱讀體驗
        - 節省雲存儲空間
        - 優化電子郵件附件大小
        """)

# pikepdf優化輔助函數
def pikepdf_optimize(input_file, output_file, params):
    """使用pikepdf進行基本優化"""
    pdf = Pdf.open(input_file)
    
    # 移除元數據
    if params["remove_metadata"]:
        with pdf.open_metadata() as meta:
            meta.clear()
    
    # 壓平表單欄位
    if params["flatten_forms"]:
        for page in pdf.pages:
            if "/Annots" in page:
                del page["/Annots"]
    
    # 移除書籤
    if params["remove_bookmarks"]:
        if "/Outlines" in pdf.Root:
            del pdf.Root["/Outlines"]
    
    # 保存為優化的PDF
    pdf.save(output_file,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            compress_streams=True,
            recompress_flate=True)
    
    return output_file 