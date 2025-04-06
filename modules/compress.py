import streamlit as st
import os
import tempfile
import subprocess
import base64
import shutil
from PyPDF2 import PdfReader
import pikepdf
from pikepdf import Pdf
import time

# 檢查Ghostscript是否可用的函數（適用於所有平台，尤其是Linux）
def check_ghostscript():
    try:
        # 直接嘗試執行gs命令
        result = subprocess.run(["gs", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, "gs", result.stdout.strip()
        
        # 如果直接執行失敗，嘗試其他可能的路徑
        for cmd in ["gswin64c", "gswin32c"]:
            try:
                result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return True, cmd, result.stdout.strip()
            except:
                pass
        
        return False, None, None
    except Exception as e:
        return False, None, str(e)

# 設置Ghostscript路徑
# 首先嘗試命令行檢測
GS_AVAILABLE, GS_CMD, GS_VERSION = check_ghostscript()

if GS_AVAILABLE:
    GHOSTSCRIPT_PATH = GS_CMD
    GHOSTSCRIPT_AVAILABLE = True
else:
    # 如果命令行檢測失敗，回退到傳統路徑檢測
    GHOSTSCRIPT_PATH = os.path.join(os.getcwd(), "gs10.05.0", "bin", "gswin64c.exe")
    if not os.path.exists(GHOSTSCRIPT_PATH):
        GHOSTSCRIPT_PATH = os.path.join(os.getcwd(), "gs10.05.0", "bin", "gswin32c.exe")
        if not os.path.exists(GHOSTSCRIPT_PATH):
            # 嘗試在系統路徑中查找
            GHOSTSCRIPT_PATH = shutil.which("gswin64c") or shutil.which("gswin32c") or shutil.which("gs") or "gs"
            
    # 最後檢查路徑是否可用
    try:
        result = subprocess.run([GHOSTSCRIPT_PATH, "--version"], capture_output=True, text=True, timeout=5)
        GHOSTSCRIPT_AVAILABLE = result.returncode == 0
    except:
        GHOSTSCRIPT_AVAILABLE = False

def pdf_compress_page():
    st.header("🔎 PDF壓縮與優化")
    st.write("壓縮和優化PDF文件，減小大小並提升性能")
    
    # 顯示Ghostscript檢測狀態
    gs_status = st.sidebar.container()
    with gs_status:
        st.subheader("系統診斷信息")
        if GHOSTSCRIPT_AVAILABLE:
            st.success(f"✅ Ghostscript 已檢測到: {GHOSTSCRIPT_PATH}")
            if GS_VERSION:
                st.info(f"Ghostscript 版本: {GS_VERSION}")
            else:
                try:
                    result = subprocess.run([GHOSTSCRIPT_PATH, "--version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        st.info(f"Ghostscript 版本: {result.stdout.strip()}")
                except Exception as e:
                    st.warning(f"無法獲取 Ghostscript 版本信息: {str(e)}")
        else:
            st.error("❌ Ghostscript 未檢測到，這可能會影響壓縮功能")
            st.info("系統路徑變量 PATH: " + os.environ.get('PATH', '未設置'))
            st.markdown("""
            **安裝 Ghostscript:**
            - Windows: 下載並安裝 [Ghostscript](https://ghostscript.com/releases/gsdnld.html)
            - macOS: 使用 Homebrew 安裝 `brew install ghostscript`
            - Linux: 使用包管理器安裝 `apt-get install ghostscript` 或 `yum install ghostscript`
            """)
            
            # 嘗試診斷問題
            st.subheader("問題診斷")
            if st.button("嘗試手動檢測Ghostscript"):
                try:
                    # 嘗試使用which命令定位gs
                    result = subprocess.run(["which", "gs"], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        gs_path = result.stdout.strip()
                        st.code(f"找到gs路徑: {gs_path}")
                        
                        # 嘗試執行找到的gs
                        try:
                            ver_result = subprocess.run([gs_path, "--version"], capture_output=True, text=True)
                            if ver_result.returncode == 0:
                                st.success(f"找到的gs可以執行，版本: {ver_result.stdout.strip()}")
                                st.info("請重新載入頁面，系統可能會重新檢測到Ghostscript")
                        except Exception as e:
                            st.error(f"執行找到的gs時出錯: {str(e)}")
                except Exception as e:
                    st.error(f"診斷Ghostscript時出錯: {str(e)}")
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        # 顯示文件信息
        st.write(f"文件名: {uploaded_file.name}")
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.write(f"原始大小: {file_size_mb:.2f} MB")
        
        # 處理選項選擇
        compress_tab, target_size_tab, advanced_tab = st.tabs(["標準壓縮", "目標大小壓縮", "高級選項"])
        
        with compress_tab:
            # 壓縮選項
            st.subheader("選擇壓縮級別")
            compression_level = st.select_slider(
                "壓縮強度",
                options=["輕度", "中度", "強力", "極限"],
                value="中度"
            )
            
            # 根據選項設置不同的壓縮方式
            compression_settings = {
                "輕度": {"dpi": 150, "image_quality": "/default", "color_mode": "Color", "metadata": False},
                "中度": {"dpi": 120, "image_quality": "/ebook", "color_mode": "Color", "metadata": True},
                "強力": {"dpi": 90, "image_quality": "/printer", "color_mode": "Color", "metadata": True},
                "極限": {"dpi": 72, "image_quality": "/screen", "color_mode": "Gray", "metadata": True}
            }
            
            # 選擇標準模式的處理選項
            remove_metadata = st.checkbox("移除元數據", value=compression_settings[compression_level]["metadata"], help="刪除文檔的額外信息以減小大小")
            
            # 應用文檔優化選項
            st.write("文檔優化選項:")
            col1, col2 = st.columns(2)
            with col1:
                flatten_forms = st.checkbox("壓平表單欄位", value=False, help="將表單欄位轉換為普通文本")
                optimize_fonts = st.checkbox("優化字體", value=True, help="優化字體以減小文件大小")
            with col2:
                remove_bookmarks = st.checkbox("移除書籤", value=False, help="刪除文檔書籤")
        
        with target_size_tab:
            st.subheader("目標大小壓縮")
            st.write("指定您想要的PDF大小，系統將自動調整參數以達到目標")
            
            # 目標大小設定 (MB)
            target_size = st.number_input(
                "目標文件大小 (MB)",
                min_value=0.1,
                max_value=float(file_size_mb),
                value=min(float(file_size_mb) * 0.5, float(file_size_mb)),
                step=0.1,
                format="%.1f",
                help="設定您希望壓縮後的文件大小（以MB為單位）"
            )
            
            # 壓縮準確度
            compression_precision = st.slider(
                "壓縮準確度",
                min_value=1,
                max_value=5,
                value=3,
                help="設定越高，壓縮結果越接近目標大小，但處理時間更長"
            )
            
            # 最大嘗試次數
            max_attempts = compression_precision * 2
            
            # 設定目標壓縮率
            target_ratio = ((file_size_mb - target_size) / file_size_mb) * 100
            st.write(f"目標壓縮率: {target_ratio:.1f}%")
        
        with advanced_tab:
            st.subheader("高級壓縮選項")
            
            # 顏色模式
            color_mode = st.radio(
                "顏色模式",
                ["彩色", "灰度", "黑白"],
                index=0,
                help="灰度或黑白模式可以顯著減小大小，但會丟失顏色信息"
            )
            
            # 圖像分辨率
            custom_dpi = st.slider(
                "圖像分辨率(DPI)",
                min_value=30,
                max_value=300,
                value=120,
                step=10,
                help="較低的分辨率可以顯著減小文件大小，但可能降低圖像質量"
            )
            
            # PDF兼容性
            pdf_version = st.selectbox(
                "PDF版本兼容性",
                ["1.4 (Acrobat 5)", "1.5 (Acrobat 6)", "1.6 (Acrobat 7)", "1.7 (Acrobat 8)"],
                index=0,
                help="較低版本兼容性可以支持更多設備，但可能限制功能"
            )
            
            # 映射PDF版本
            pdf_version_map = {
                "1.4 (Acrobat 5)": "1.4",
                "1.5 (Acrobat 6)": "1.5",
                "1.6 (Acrobat 7)": "1.6",
                "1.7 (Acrobat 8)": "1.7"
            }
            
            # 結構優化選項
            remove_unused = st.checkbox("移除未使用的對象", value=True, help="清理文檔中未使用的對象以減小大小")
            
        # 確定壓縮方法
        compression_method = st.radio(
            "選擇處理方式",
            ["標準壓縮", "目標大小壓縮", "高級自定義壓縮"],
            horizontal=True,
            index=0
        )
        
        # 壓縮按鈕
        if st.button("壓縮PDF"):
            with st.spinner("正在處理PDF..."):
                try:
                    # 創建臨時目錄處理文件
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        # 使用短文件名和路徑避免特殊字符問題
                        temp_input = os.path.join(tmpdirname, "input.pdf")
                        temp_output = os.path.join(tmpdirname, "output.pdf")
                        
                        # 寫入臨時文件
                        with open(temp_input, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # 讀取文件基本信息
                        reader = PdfReader(temp_input)
                        total_pages = len(reader.pages)
                        
                        # 根據選擇的方法執行不同的壓縮策略
                        if compression_method == "標準壓縮":
                            # 使用標準壓縮選項卡的設置
                            gs_params = compression_settings[compression_level]
                            
                            # 進行文檔處理
                            compressed_file = process_pdf(
                                temp_input, 
                                temp_output, 
                                dpi=gs_params["dpi"],
                                image_quality=gs_params["image_quality"],
                                color_mode=gs_params["color_mode"],
                                remove_metadata=remove_metadata,
                                flatten_forms=flatten_forms,
                                remove_bookmarks=remove_bookmarks,
                                optimize_fonts=optimize_fonts,
                                pdf_version=pdf_version_map["1.4 (Acrobat 5)"],
                                remove_unused=True
                            )
                            
                        elif compression_method == "目標大小壓縮":
                            # 目標大小壓縮，進行反覆嘗試以接近目標
                            compressed_file = target_size_compression(
                                temp_input,
                                tmpdirname,
                                target_size,
                                max_attempts,
                                total_pages
                            )
                        
                        else:  # 高級自定義壓縮
                            # 顏色設置映射
                            color_settings = {"彩色": "Color", "灰度": "Gray", "黑白": "Mono"}
                            
                            # 進行文檔處理
                            compressed_file = process_pdf(
                                temp_input, 
                                temp_output, 
                                dpi=custom_dpi,
                                image_quality="/default",
                                color_mode=color_settings[color_mode],
                                remove_metadata=True,
                                flatten_forms=flatten_forms,
                                remove_bookmarks=remove_bookmarks,
                                optimize_fonts=optimize_fonts,
                                pdf_version=pdf_version_map[pdf_version],
                                remove_unused=remove_unused
                            )
                        
                        # 檢查輸出文件是否存在且大小正常
                        if compressed_file and os.path.exists(compressed_file) and os.path.getsize(compressed_file) > 0:
                            compressed_size_mb = os.path.getsize(compressed_file) / (1024 * 1024)
                            
                            # 計算壓縮率
                            compression_ratio = ((file_size_mb - compressed_size_mb) / file_size_mb) * 100
                            
                            # 輸出結果展示
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("原始大小", f"{file_size_mb:.2f} MB", "")
                            with col2:
                                st.metric("壓縮後大小", f"{compressed_size_mb:.2f} MB", "")
                            with col3:
                                st.metric("節省空間", f"{compression_ratio:.1f}%", f"-{file_size_mb - compressed_size_mb:.2f} MB")
                            
                            # 進度條顯示壓縮比例
                            st.progress(min(compression_ratio / 100, 1.0))
                            
                            # 顯示壓縮信息
                            if compression_ratio > 0:
                                if compression_method == "目標大小壓縮" and abs(compressed_size_mb - target_size) <= 0.2:
                                    st.success(f"🎯 成功壓縮PDF至接近目標大小: {compressed_size_mb:.2f} MB (目標: {target_size:.2f} MB)")
                                else:
                                    st.success(f"✅ 成功壓縮PDF文件，減少了 {compression_ratio:.1f}% 的大小")
                            else:
                                st.info("⚠️ 文件已處理，但壓縮效果有限")
                            
                            # 創建下載按鈕
                            with open(compressed_file, "rb") as f:
                                pdf_bytes = f.read()
                            
                            base_name = os.path.splitext(uploaded_file.name)[0]
                            download_name = f"{base_name}_compressed.pdf"
                            
                            b64_pdf = base64.b64encode(pdf_bytes).decode()
                            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{download_name}" class="download-button">下載處理後的PDF</a>'
                            st.markdown(href, unsafe_allow_html=True)
                            
                            # 顯示壓縮設置的摘要
                            with st.expander("處理參數摘要"):
                                st.write(f"• 壓縮方法: {compression_method}")
                                if compression_method == "標準壓縮":
                                    st.write(f"• 壓縮級別: {compression_level}")
                                    st.write(f"• 圖像分辨率: {gs_params['dpi']} DPI")
                                    st.write(f"• 移除元數據: {'是' if remove_metadata else '否'}")
                                    st.write(f"• 壓平表單欄位: {'是' if flatten_forms else '否'}")
                                    st.write(f"• 移除書籤: {'是' if remove_bookmarks else '否'}")
                                    st.write(f"• 優化字體: {'是' if optimize_fonts else '否'}")
                                elif compression_method == "目標大小壓縮":
                                    st.write(f"• 目標大小: {target_size:.2f} MB")
                                    st.write(f"• 壓縮準確度: {compression_precision}")
                                else:
                                    st.write(f"• 顏色模式: {color_mode}")
                                    st.write(f"• 圖像分辨率: {custom_dpi} DPI")
                                    st.write(f"• PDF版本: {pdf_version}")
                                st.write(f"• 總頁數: {total_pages}")
                        else:
                            st.error("壓縮過程中發生錯誤，無法創建輸出文件")
                            st.warning("請嘗試使用不同的壓縮設置或檢查文件格式")
                except Exception as e:
                    st.error(f"處理過程中出錯: {str(e)}")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件進行處理")
        
        # 檢查Ghostscript是否存在
        gs_exists = os.path.exists(GHOSTSCRIPT_PATH) 
        if gs_exists:
            st.success(f"已檢測到Ghostscript: {GHOSTSCRIPT_PATH}")
        else:
            st.warning("未檢測到Ghostscript，壓縮功能可能受限")
            st.info("建議安裝Ghostscript以獲得最佳壓縮效果")
        
        st.markdown("""
        ### 使用說明
        1. 上傳您要壓縮的PDF文件
        2. 選擇處理方式：
           - **標準壓縮**：選擇預設壓縮級別
           - **目標大小壓縮**：指定您需要的文件大小
           - **高級自定義壓縮**：手動調整所有參數
        3. 點擊"壓縮PDF"按鈕
        4. 下載處理後的文件
        
        ### 功能亮點
        - **智能壓縮**：根據文件內容自動調整參數
        - **目標大小壓縮**：自動調整壓縮參數直到達到指定大小
        - **高級結構優化**：不僅壓縮圖片，還優化PDF內部結構
        
        ### 適用場景
        - 發送郵件時需要縮小附件大小
        - 節省雲存儲空間
        - 減少文件傳輸時間
        - 優化網站上的PDF文檔大小
        """)

# 目標大小壓縮函數
def target_size_compression(input_file, temp_dir, target_size_mb, max_attempts, total_pages):
    """
    通過多次嘗試接近目標大小的壓縮方法，只調整DPI和壓縮品質，保留原始顏色
    """
    # 初始參數
    current_dpi = 150
    current_quality = "/default"
    
    # 嘗試不同的壓縮參數組合
    attempts = 0
    best_file = None
    best_diff = float('inf')
    
    # 顯示進度條
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    # 根據頁數和目標壓縮率確定DPI值範圍
    file_size_mb = os.path.getsize(input_file) / (1024 * 1024)
    compression_ratio = ((file_size_mb - target_size_mb) / file_size_mb) * 100
    
    # 根據目標壓縮率選擇合適的DPI範圍
    if compression_ratio > 80:  # 極度壓縮
        dpi_values = [72, 60, 50, 40, 30]
    elif compression_ratio > 60:  # 高度壓縮
        dpi_values = [90, 80, 72, 60, 50]
    elif compression_ratio > 40:  # 中度壓縮
        dpi_values = [110, 100, 90, 80, 72]
    elif compression_ratio > 20:  # 輕度壓縮
        dpi_values = [130, 120, 110, 100, 90]
    else:  # 微度壓縮
        dpi_values = [150, 140, 130, 120, 110]
    
    # 壓縮品質選項
    quality_values = ["/default", "/ebook", "/printer", "/screen"]
    
    # 生成嘗試列表，只使用彩色模式
    attempts_list = []
    for dpi in dpi_values:
        for quality in quality_values:
            attempts_list.append((dpi, quality, "Color"))
    
    # 限制嘗試次數
    attempts_list = attempts_list[:max_attempts]
    
    # 創建一個專門用於測試的輸入文件副本
    test_input_file = os.path.join(temp_dir, "test_input.pdf")
    shutil.copy2(input_file, test_input_file)
    
    # 開始嘗試
    for i, (dpi, quality, color) in enumerate(attempts_list):
        attempts += 1
        
        # 更新進度
        progress = (i + 1) / len(attempts_list)
        progress_bar.progress(progress)
        progress_text.text(f"嘗試設置組合 {i+1}/{len(attempts_list)}: DPI={dpi}, 質量={quality}")
        
        # 每次嘗試都使用唯一的輸出文件名
        temp_output = os.path.join(temp_dir, f"attempt_{attempts}.pdf")
        
        # 處理文件
        processed_file = process_pdf(
            test_input_file, 
            temp_output, 
            dpi=dpi,
            image_quality=quality,
            color_mode="Color",  # 始終使用彩色模式
            remove_metadata=True,
            flatten_forms=True,
            remove_bookmarks=True,
            optimize_fonts=True,
            pdf_version="1.4",  # 使用兼容性最好的版本
            remove_unused=True
        )
        
        if processed_file and os.path.exists(processed_file):
            # 計算與目標大小的差距
            current_size_mb = os.path.getsize(processed_file) / (1024 * 1024)
            diff = abs(current_size_mb - target_size_mb)
            
            # 更新進度文本
            progress_text.text(f"嘗試 {i+1}/{len(attempts_list)} - 當前大小: {current_size_mb:.2f}MB (目標: {target_size_mb:.2f}MB)")
            
            # 如果是最佳結果，保存它
            if diff < best_diff:
                best_diff = diff
                if best_file and best_file != processed_file and os.path.exists(best_file):
                    try:
                        os.remove(best_file)  # 刪除之前的最佳文件
                    except:
                        pass
                best_file = processed_file
            
            # 目標大小接近時提前退出
            if diff < 0.05 or current_size_mb <= target_size_mb:
                progress_text.text(f"✅ 已達到目標大小或足夠接近 - 實際大小: {current_size_mb:.2f}MB")
                break
    
    # 清空進度提示
    progress_text.empty()
    
    # 清理測試文件
    try:
        if os.path.exists(test_input_file):
            os.remove(test_input_file)
    except:
        pass
    
    return best_file

# PDF處理函數
def process_pdf(input_file, output_file, dpi=120, image_quality="/default", color_mode="Color", 
               remove_metadata=True, flatten_forms=False, remove_bookmarks=False, 
               optimize_fonts=True, pdf_version="1.4", remove_unused=True):
    """
    使用Ghostscript或pikepdf處理PDF的綜合函數
    """
    if GHOSTSCRIPT_AVAILABLE:
        # 使用Ghostscript處理
        try:
            # 確保路徑沒有問題，轉換為適當的格式
            output_path = output_file.replace('\\', '/')
            input_path = input_file.replace('\\', '/')
            
            # 設置Ghostscript命令
            gs_cmd = [
                GHOSTSCRIPT_PATH,
                "-sDEVICE=pdfwrite",
                f"-dCompatibilityLevel={pdf_version}",
                f"-dPDFSETTINGS={image_quality}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-r{dpi}"
            ]
            
            # 添加顏色模式設置
            if color_mode == "Gray":
                gs_cmd.append("-sColorConversionStrategy=Gray")
                gs_cmd.append("-dProcessColorModel=/DeviceGray")
            elif color_mode == "Mono":
                gs_cmd.append("-sColorConversionStrategy=Mono")
                gs_cmd.append("-dProcessColorModel=/DeviceGray")
            
            # 添加元數據處理
            if remove_metadata:
                gs_cmd.append("-dFastWebView=true")
            
            # 添加優化選項
            if remove_unused:
                gs_cmd.append("-dDetectDuplicateImages=true")
                gs_cmd.append("-dCompressFonts=true")
            
            if optimize_fonts:
                gs_cmd.append("-dEmbedAllFonts=false")
                gs_cmd.append("-dSubsetFonts=true")
            
            # 添加輸出和輸入文件，放在命令末尾
            gs_cmd.append(f"-sOutputFile={output_path}")
            gs_cmd.append(input_path)
            
            # 執行Ghostscript命令
            process = subprocess.run(
                gs_cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 處理表單和書籤需要進一步處理
            if flatten_forms or remove_bookmarks:
                pikepdf_optimize(output_file, output_file, {
                    "flatten_forms": flatten_forms,
                    "remove_bookmarks": remove_bookmarks,
                    "remove_metadata": False,  # 已由GS處理
                    "optimize_fonts": False    # 已由GS處理
                })
            
            return output_file
            
        except Exception as e:
            st.warning(f"Ghostscript處理失敗: {str(e)}，使用備用方法...")
            # 如果Ghostscript失敗，回退到pikepdf
            return pikepdf_optimize(input_file, output_file, {
                "remove_metadata": remove_metadata,
                "flatten_forms": flatten_forms,
                "remove_bookmarks": remove_bookmarks,
                "optimize_fonts": optimize_fonts
            })
    else:
        # 沒有Ghostscript，使用pikepdf
        return pikepdf_optimize(input_file, output_file, {
            "remove_metadata": remove_metadata,
            "flatten_forms": flatten_forms,
            "remove_bookmarks": remove_bookmarks,
            "optimize_fonts": optimize_fonts
        })

# pikepdf優化輔助函數
def pikepdf_optimize(input_file, output_file, params):
    """使用pikepdf進行基本優化"""
    try:
        # 檢查輸入和輸出路徑是否相同
        if os.path.abspath(input_file) == os.path.abspath(output_file):
            pdf = Pdf.open(input_file, allow_overwriting_input=True)
        else:
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
    except Exception as e:
        st.error(f"pikepdf處理時出錯: {str(e)}")
        return None 