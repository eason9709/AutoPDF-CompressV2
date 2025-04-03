import streamlit as st
import os
import tempfile
import base64
from io import BytesIO
from pdf2image import convert_from_path
from PIL import Image
import shutil

def legacy_compress_page():
    st.header("⚙️ 舊版PDF壓縮工具")
    st.write("使用圖像轉換方式壓縮PDF文件，適合需精確控制輸出大小的場景")
    
    # 檢查是否已安裝poppler
    try:
        from pdf2image.pdf2image import pdfinfo_from_path
        poppler_installed = True
    except Exception:
        poppler_installed = False
    
    if not poppler_installed:
        st.error("此功能需要安裝Poppler! 請參考以下說明進行安裝：")
        
        with st.expander("Poppler安裝指南", expanded=True):
            st.markdown("""
            ### Windows用戶
            1. 下載Poppler: [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
            2. 解壓檔案到您的電腦，例如 `C:\\Program Files\\poppler`
            3. 添加Poppler的bin目錄到系統PATH變數（例如 `C:\\Program Files\\poppler\\bin`）
            
            ### macOS用戶
            使用Homebrew安裝：
            ```
            brew install poppler
            ```
            
            ### Linux用戶
            使用apt安裝：
            ```
            sudo apt-get install poppler-utils
            ```
            
            安裝完成後請重新啟動應用。
            """)
        return
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇要壓縮的PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 保存上傳的文件
            input_file = os.path.join(tmpdirname, uploaded_file.name)
            with open(input_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 檢查文件大小
            original_size = os.path.getsize(input_file) / 1024  # KB
            st.write(f"原始檔案大小: {original_size:.2f} KB")
            
            # 壓縮設定
            st.subheader("壓縮設定")
            
            col1, col2 = st.columns(2)
            with col1:
                # DPI 設定
                dpi = st.slider("DPI設定", min_value=72, max_value=300, value=200, 
                                help="較低的DPI產生較小的文件，但可能降低品質")
            
            with col2:
                # 自動模式
                auto_mode = st.checkbox("自動調整DPI以達到目標大小", value=False,
                                      help="自動降低DPI直到文件大小低於目標值")
                
                if auto_mode:
                    target_size = st.number_input("目標檔案大小 (KB)", 
                                               min_value=100, max_value=10000, value=4096)
            
            # 預覽
            with st.expander("處理預覽", expanded=False):
                st.write("此功能將PDF轉換為圖像，再組合為新的PDF，適合掃描文檔和以圖像為主的PDF。")
                st.write("優點：可精確控制輸出大小，特別適合需要符合上傳大小限制的場景。")
                st.write("缺點：可能導致文本無法選取，不適合純文字PDF。")
            
            # 壓縮按鈕
            if st.button("開始壓縮"):
                with st.spinner("正在處理中..."):
                    try:
                        output_path = os.path.join(tmpdirname, f"compressed_{uploaded_file.name}")
                        
                        if auto_mode:
                            # 自動調整模式
                            # 先使用較低DPI嘗試獲得小於目標大小的結果
                            current_dpi = min(dpi, 150)  # 以較低DPI開始
                            max_attempts = 15  # 增加嘗試次數以獲得更精確的結果
                            attempt = 0
                            
                            # 階段1: 找到一個小於目標大小的DPI
                            last_success_dpi = 0
                            last_success_size = 0
                            
                            while attempt < max_attempts:
                                attempt += 1
                                st.write(f"嘗試 #{attempt}，使用DPI: {current_dpi}")
                                
                                # 轉換PDF為圖像
                                images = convert_from_path(input_file, dpi=current_dpi)
                                jpg_files = []
                                
                                # 保存為臨時JPG文件
                                for i, image in enumerate(images):
                                    jpg_path = os.path.join(tmpdirname, f"temp_page_{i}.jpg")
                                    image = image.convert("RGB")
                                    image.save(jpg_path, 'JPEG')
                                    jpg_files.append(jpg_path)
                                
                                # 創建新的PDF
                                image_objects = [Image.open(jpg_file) for jpg_file in jpg_files]
                                if image_objects:
                                    image_objects[0].save(
                                        output_path, 
                                        save_all=True, 
                                        append_images=image_objects[1:] if len(image_objects) > 1 else []
                                    )
                                
                                # 清理臨時文件
                                for jpg_file in jpg_files:
                                    os.remove(jpg_file)
                                
                                # 檢查輸出大小
                                output_size = os.path.getsize(output_path) / 1024  # KB
                                
                                if output_size <= target_size:
                                    # 達到了目標大小以下，記錄這個DPI和大小
                                    last_success_dpi = current_dpi
                                    last_success_size = output_size
                                    
                                    # 結束條件: 已達到最小DPI或已非常接近目標大小
                                    if current_dpi >= 300 or (target_size - output_size) < target_size * 0.05:
                                        st.write("已找到最佳DPI設定")
                                        break
                                        
                                    # 嘗試更高一點的DPI，看能否更接近目標大小
                                    next_dpi = min(300, int(current_dpi * 1.1))
                                    if next_dpi == current_dpi:
                                        next_dpi += 5  # 確保至少增加一點
                                    current_dpi = next_dpi
                                else:
                                    # 超過目標大小，需要降低DPI
                                    if last_success_dpi > 0:
                                        # 我們之前已找到一個成功的DPI，找最大的可行值
                                        current_dpi = int((last_success_dpi + current_dpi) / 2)
                                        # 如果差距很小，就結束嘗試
                                        if abs(current_dpi - last_success_dpi) <= 2:
                                            current_dpi = last_success_dpi
                                            output_size = last_success_size
                                            st.write(f"確定最終DPI: {current_dpi}")
                                            break
                                    else:
                                        # 首次嘗試就超過目標大小，大幅降低DPI
                                        size_ratio = output_size / target_size
                                        current_dpi = max(72, int(current_dpi / size_ratio))
                                        
                            # 如果沒有找到合適的值，使用最後一次成功的設定
                            if last_success_dpi > 0 and output_size > target_size:
                                st.write(f"使用之前找到的最佳DPI: {last_success_dpi}")
                                current_dpi = last_success_dpi
                                
                                # 重新生成一次PDF以確保大小正確
                                images = convert_from_path(input_file, dpi=current_dpi)
                                jpg_files = []
                                for i, image in enumerate(images):
                                    jpg_path = os.path.join(tmpdirname, f"temp_page_{i}.jpg")
                                    image = image.convert("RGB")
                                    image.save(jpg_path, 'JPEG')
                                    jpg_files.append(jpg_path)
                                
                                image_objects = [Image.open(jpg_file) for jpg_file in jpg_files]
                                if image_objects:
                                    image_objects[0].save(
                                        output_path, 
                                        save_all=True, 
                                        append_images=image_objects[1:] if len(image_objects) > 1 else []
                                    )
                                
                                for jpg_file in jpg_files:
                                    os.remove(jpg_file)
                                    
                                output_size = os.path.getsize(output_path) / 1024  # KB
                        else:
                            # 標準模式
                            # 轉換PDF為圖像
                            images = convert_from_path(input_file, dpi=dpi)
                            jpg_files = []
                            
                            # 保存為臨時JPG文件
                            for i, image in enumerate(images):
                                jpg_path = os.path.join(tmpdirname, f"temp_page_{i}.jpg")
                                image = image.convert("RGB")
                                image.save(jpg_path, 'JPEG')
                                jpg_files.append(jpg_path)
                            
                            # 創建新的PDF
                            image_objects = [Image.open(jpg_file) for jpg_file in jpg_files]
                            if image_objects:
                                image_objects[0].save(
                                    output_path, 
                                    save_all=True, 
                                    append_images=image_objects[1:] if len(image_objects) > 1 else []
                                )
                            
                            # 清理臨時文件
                            for jpg_file in jpg_files:
                                os.remove(jpg_file)
                        
                        # 顯示結果
                        output_size = os.path.getsize(output_path) / 1024  # KB
                        reduction = (1 - output_size / original_size) * 100
                        
                        st.success(f"壓縮完成！")
                        st.write(f"原始大小: {original_size:.2f} KB")
                        st.write(f"壓縮後大小: {output_size:.2f} KB")
                        st.write(f"減少: {reduction:.1f}%")
                        
                        # 提供的DPI
                        if auto_mode:
                            st.write(f"最終使用的DPI: {current_dpi}")
                        
                        # 提供下載
                        with open(output_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        download_filename = f"compressed_{uploaded_file.name}"
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{download_filename}" class="download-button">下載壓縮後的PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    
                    except Exception as e:
                        st.error(f"處理過程中出錯: {str(e)}")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件")
        
        st.markdown("""
        ### 舊版壓縮工具說明
        
        這是基於圖像轉換的傳統PDF壓縮方法，專為以下場景設計：
        
        - 需要精確控制輸出文件大小（例如上傳大小有嚴格限制）
        - 主要包含掃描內容或圖像的PDF
        - 不關心文本可選性，只需保留視覺內容
        
        ### 使用方法
        
        1. 上傳PDF文件
        2. 手動設置DPI值（較低值 = 較小文件 + 較低質量）
        3. 或啟用自動模式，設置目標文件大小
           - 自動模式會嘗試產生**最接近但不超過**目標大小的文件
           - 系統會自動尋找最高可能的DPI值，以保持最佳圖像質量
        4. 點擊"開始壓縮"按鈕
        5. 下載壓縮後的文件
        
        ### 技術說明
        
        此工具將PDF轉換為圖像，然後重新組合為新的PDF。這種方法可以顯著減小文件大小，但會將所有內容轉為光柵圖像，使文本不可選擇，不適合需要保留文檔結構的場景。
        
        ### 注意事項
        
        此功能需要安裝Poppler庫。如果您遇到"需要安裝Poppler"的錯誤，請參照安裝指南進行安裝。
        """) 