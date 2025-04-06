import streamlit as st
import os
import tempfile
import zipfile
from pdf2image import convert_from_path
import base64
from io import BytesIO
from PIL import Image

def pdf_to_image_page():
    st.header("🖼️ PDF轉圖片")
    st.write("將PDF頁面轉換為圖片格式")
    
    # 嘗試找到Poppler路徑
    poppler_paths = [
        "/usr/bin",
        "/usr/local/bin",
        "/usr/lib/x86_64-linux-gnu/poppler",
        "/usr/lib/poppler"
    ]
    
    poppler_path = None
    for path in poppler_paths:
        if os.path.exists(os.path.join(path, "pdftoppm")) or os.path.exists(path + "/pdftoppm"):
            poppler_path = path
            st.success(f"找到Poppler在: {poppler_path}")
            break
    
    # 如果在標準路徑中找不到，嘗試用which命令查找
    if poppler_path is None:
        try:
            import subprocess
            result = subprocess.run(["which", "pdftoppm"], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pdftoppm_path = result.stdout.strip()
                poppler_path = os.path.dirname(pdftoppm_path)
                st.success(f"找到Poppler在: {poppler_path}")
        except Exception as e:
            st.warning(f"查找pdftoppm路徑時出錯: {str(e)}")
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 保存上傳的文件
            temp_file = os.path.join(tmpdirname, uploaded_file.name)
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # 獲取PDF頁數
            try:
                from PyPDF2 import PdfReader
                pdf = PdfReader(temp_file)
                total_pages = len(pdf.pages)
                
                st.write(f"文件名: {uploaded_file.name}")
                st.write(f"總頁數: {total_pages}")
                
                # 設置轉換選項
                st.subheader("轉換選項")
                
                # 選擇要轉換的頁面
                page_selection = st.radio(
                    "選擇要轉換的頁面",
                    ["所有頁面", "特定頁面"]
                )
                
                if page_selection == "特定頁面":
                    page_ranges = st.text_input(
                        "指定頁數範圍（例如：1-5,7,9-12）",
                        value="1"
                    )
                
                # 選擇圖片格式
                image_format = st.selectbox(
                    "圖片格式",
                    ["PNG", "JPEG", "TIFF", "BMP"]
                )
                
                # DPI設置
                dpi = st.slider(
                    "圖像DPI (解析度)",
                    min_value=72,
                    max_value=600,
                    value=200,
                    step=10
                )
                
                # 圖像質量（僅適用於JPEG）
                if image_format == "JPEG":
                    quality = st.slider(
                        "JPEG質量",
                        min_value=10,
                        max_value=100,
                        value=80,
                        step=5
                    )
                else:
                    quality = 80  # 默認值
                
                # 開始轉換按鈕
                if st.button("轉換為圖片"):
                    with st.spinner("正在轉換PDF頁面為圖片..."):
                        try:
                            # 確定要轉換的頁面
                            if page_selection == "所有頁面":
                                page_nums = list(range(1, total_pages + 1))
                            else:
                                page_nums = []
                                parts = page_ranges.split(',')
                                for part in parts:
                                    if '-' in part:
                                        start, end = map(int, part.split('-'))
                                        # 檢查範圍是否有效
                                        if start < 1 or end > total_pages or start > end:
                                            st.error(f"無效的頁數範圍: {part}")
                                            break
                                        page_nums.extend(list(range(start, end + 1)))
                                    else:
                                        page = int(part)
                                        if page < 1 or page > total_pages:
                                            st.error(f"無效的頁數: {part}")
                                            break
                                        page_nums.append(page)
                            
                            # 創建保存圖片的目錄
                            image_dir = os.path.join(tmpdirname, "images")
                            os.makedirs(image_dir, exist_ok=True)
                            
                            # 轉換PDF頁面為圖片，使用找到的poppler_path
                            images = convert_from_path(
                                temp_file, 
                                dpi=dpi, 
                                first_page=min(page_nums),
                                last_page=max(page_nums),
                                poppler_path=poppler_path
                            )
                            
                            # 儲存圖片
                            image_paths = []
                            for i, image in enumerate(images):
                                page_num = page_nums[i] if i < len(page_nums) else min(page_nums) + i
                                
                                # 根據選擇的格式設置文件名和格式
                                if image_format == "PNG":
                                    img_file = os.path.join(image_dir, f"page_{page_num}.png")
                                    image.save(img_file, "PNG")
                                elif image_format == "JPEG":
                                    img_file = os.path.join(image_dir, f"page_{page_num}.jpg")
                                    image.save(img_file, "JPEG", quality=quality)
                                elif image_format == "TIFF":
                                    img_file = os.path.join(image_dir, f"page_{page_num}.tiff")
                                    image.save(img_file, "TIFF")
                                elif image_format == "BMP":
                                    img_file = os.path.join(image_dir, f"page_{page_num}.bmp")
                                    image.save(img_file, "BMP")
                                
                                image_paths.append(img_file)
                            
                            # 創建圖片預覽
                            st.subheader("圖片預覽")
                            cols = st.columns(min(3, len(image_paths)))
                            for idx, img_path in enumerate(image_paths[:6]):  # 最多顯示6張圖片預覽
                                with cols[idx % 3]:
                                    img = Image.open(img_path)
                                    st.image(img, caption=f"頁面 {page_nums[idx]}", width=200)
                            
                            if len(image_paths) > 6:
                                st.info(f"只顯示前6張圖片預覽，總共轉換了 {len(image_paths)} 張圖片")
                            
                            # 創建ZIP文件
                            zip_file = os.path.join(tmpdirname, "converted_images.zip")
                            with zipfile.ZipFile(zip_file, 'w') as zipf:
                                for img_path in image_paths:
                                    zipf.write(img_path, os.path.basename(img_path))
                            
                            # 提供下載
                            with open(zip_file, "rb") as f:
                                zip_bytes = f.read()
                            
                            b64_zip = base64.b64encode(zip_bytes).decode()
                            href = f'<a href="data:application/zip;base64,{b64_zip}" download="converted_images.zip" class="download-button">下載所有圖片</a>'
                            st.markdown(href, unsafe_allow_html=True)
                            
                            st.success(f"成功將 {len(image_paths)} 頁PDF轉換為 {image_format} 格式")
                        
                        except Exception as e:
                            st.error(f"轉換過程中出錯: {str(e)}")
                            if "poppler" in str(e).lower():
                                st.info("提示：此功能需要安裝Poppler。在Windows上，您可以下載安裝poppler-windows並添加到PATH環境變量。")
            
            except Exception as e:
                st.error(f"讀取PDF時出錯: {str(e)}")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件進行轉換")
        
        st.markdown("""
        ### 使用說明
        1. 上傳您的PDF文件
        2. 選擇要轉換的頁面（所有頁面或特定頁面）
        3. 選擇輸出圖片格式（PNG、JPEG、TIFF或BMP）
        4. 調整DPI（解析度）設置
        5. 對於JPEG格式，可以調整圖像質量
        6. 點擊"轉換為圖片"按鈕
        7. 下載包含所有圖片的ZIP壓縮包
        
        ### 適用場景
        - 提取PDF中的圖表或圖形
        - 將PDF演示文稿轉換為圖片幻燈片
        - 為不支持PDF的設備準備內容
        - 在社交媒體上分享PDF內容
        """) 