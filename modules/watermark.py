import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import sys

# 註冊中文字體
def register_fonts():
    # 註冊內置中文字體(用於支持中文水印)
    font_path = None
    
    # 根據不同操作系統查找合適的中文字體
    if sys.platform.startswith('win'):
        # Windows 系統字體路徑
        possible_fonts = [
            "C:\\Windows\\Fonts\\mingliu.ttc",
            "C:\\Windows\\Fonts\\msjh.ttc",
            "C:\\Windows\\Fonts\\simsun.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf"
        ]
    elif sys.platform.startswith('darwin'):
        # macOS 系統字體路徑
        possible_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/Library/Fonts/Microsoft/PMingLiU.ttf",
            "/Library/Fonts/Microsoft/SimHei.ttf"
        ]
    else:
        # Linux 系統字體路徑
        possible_fonts = [
            "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        ]
    
    # 檢查字體文件是否存在並註冊第一個找到的字體
    for font_file in possible_fonts:
        if os.path.exists(font_file):
            font_path = font_file
            break
    
    # 如果找到系統字體，註冊它
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
            return "ChineseFont"
        except:
            pass
    
    # 如果找不到系統字體，返回默認字體
    return "Helvetica"

# 获取默认中文字体
DEFAULT_CHINESE_FONT = register_fonts()

def pdf_watermark_page():
    st.header("🖊️ PDF水印")
    st.write("為PDF文件添加文字或圖片水印")
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 保存上傳的文件
            temp_file = os.path.join(tmpdirname, uploaded_file.name)
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 先檢查PDF是否加密
            try:
                reader = PdfReader(temp_file)
                is_encrypted = reader.is_encrypted
            except Exception as e:
                is_encrypted = True  # 假設遇到錯誤時文件可能是加密的
            
            # 如果文件已加密，顯示密碼輸入框
            password = None
            if is_encrypted:
                st.warning("這個PDF文件已加密，請輸入密碼進行解密")
                password = st.text_input("PDF密碼", type="password")
                
                if password:
                    try:
                        reader = PdfReader(temp_file)
                        if reader.is_encrypted:
                            reader.decrypt(password)
                        st.success("PDF文件解密成功！")
                        is_encrypted = False
                    except Exception as e:
                        st.error(f"解密失敗: {str(e)}")
                        st.info("請確認密碼是否正確")
                
            # 若文件沒有加密或已成功解密，繼續處理
            if not is_encrypted or (is_encrypted and password and 'reader' in locals()):
                try:
                    # 確保reader已創建
                    if 'reader' not in locals():
                        reader = PdfReader(temp_file)
                    
                    total_pages = len(reader.pages)
                    
                    st.write(f"文件名: {uploaded_file.name}")
                    st.write(f"總頁數: {total_pages}")
                    
                    # 選擇水印類型
                    st.subheader("水印設置")
                    watermark_type = st.radio(
                        "選擇水印類型",
                        ["文字水印", "圖片水印"]
                    )
                    
                    # 文字水印設置
                    if watermark_type == "文字水印":
                        watermark_text = st.text_input("水印文字", value="機密文件")
                        
                        with st.expander("文字水印選項", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # 文字大小
                                font_size = st.slider("字體大小", 10, 100, 40)
                                
                                # 文字顏色
                                color_options = {
                                    "淺灰色": (0.75, 0.75, 0.75, 0.3),
                                    "深灰色": (0.5, 0.5, 0.5, 0.3),
                                    "淺紅色": (1, 0.5, 0.5, 0.3),
                                    "淺藍色": (0.5, 0.5, 1, 0.3),
                                    "淺綠色": (0.5, 1, 0.5, 0.3)
                                }
                                color_choice = st.selectbox(
                                    "文字顏色",
                                    list(color_options.keys())
                                )
                                text_color = color_options[color_choice]
                                
                                # 添加字體選擇
                                font_options = {
                                    "預設中文字體": DEFAULT_CHINESE_FONT,
                                    "Helvetica (僅支援英文)": "Helvetica",
                                    "Courier (僅支援英文)": "Courier",
                                    "Times-Roman (僅支援英文)": "Times-Roman"
                                }
                                font_choice = st.selectbox(
                                    "字體選擇",
                                    list(font_options.keys())
                                )
                                selected_font = font_options[font_choice]
                                
                            with col2:
                                # 文字角度
                                angle = st.slider("旋轉角度", -90, 90, 45)
                                
                                # 文字間距
                                x_gap = st.slider("水平間距", 50, 500, 200)
                                y_gap = st.slider("垂直間距", 50, 500, 200)
                        
                        # 頁面選擇
                        page_selection = st.radio(
                            "應用於",
                            ["所有頁面", "僅首頁", "僅末頁", "特定頁面"]
                        )
                        
                        if page_selection == "特定頁面":
                            page_ranges = st.text_input(
                                "指定頁數範圍（例如：1-5,7,9-12）",
                                value="1"
                            )
                    
                    # 圖片水印設置
                    else:
                        uploaded_image = st.file_uploader("上傳水印圖片", type=["png", "jpg", "jpeg"])
                        
                        if uploaded_image:
                            # 顯示預覽
                            image = Image.open(uploaded_image)
                            st.image(image, caption="水印圖片預覽", width=200)
                            
                            with st.expander("圖片水印選項", expanded=True):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    # 透明度
                                    opacity = st.slider("透明度", 0.1, 1.0, 0.3, 0.05)
                                    
                                    # 水印大小
                                    size = st.slider("大小（相對於頁面寬度的百分比）", 10, 100, 30)
                                    
                                with col2:
                                    # 位置
                                    position = st.selectbox(
                                        "水印位置",
                                        ["居中", "左上角", "右上角", "左下角", "右下角"]
                                    )
                                    
                                    # 頁面選擇
                                    page_selection = st.radio(
                                        "應用於",
                                        ["所有頁面", "僅首頁", "僅末頁", "特定頁面"]
                                    )
                            
                            if page_selection == "特定頁面":
                                page_ranges = st.text_input(
                                    "指定頁數範圍（例如：1-5,7,9-12）",
                                    value="1"
                                )
                        else:
                            st.info("請上傳水印圖片")
                    
                    # 應用水印按鈕
                    if st.button("應用水印"):
                        # 檢查是否可以應用水印
                        if watermark_type == "圖片水印" and not uploaded_image:
                            st.error("請先上傳水印圖片")
                        else:
                            with st.spinner("正在應用水印..."):
                                try:
                                    # 確定要應用水印的頁面
                                    if page_selection == "所有頁面":
                                        pages_to_watermark = list(range(total_pages))
                                    elif page_selection == "僅首頁":
                                        pages_to_watermark = [0]
                                    elif page_selection == "僅末頁":
                                        pages_to_watermark = [total_pages - 1]
                                    else:  # 特定頁面
                                        pages_to_watermark = []
                                        parts = page_ranges.split(',')
                                        for part in parts:
                                            if '-' in part:
                                                start, end = map(int, part.split('-'))
                                                # 檢查範圍是否有效
                                                if start < 1 or end > total_pages or start > end:
                                                    st.error(f"無效的頁數範圍: {part}")
                                                    break
                                                pages_to_watermark.extend([i-1 for i in range(start, end + 1)])
                                            else:
                                                page = int(part)
                                                if page < 1 or page > total_pages:
                                                    st.error(f"無效的頁數: {part}")
                                                    break
                                                pages_to_watermark.append(page - 1)  # 轉換為0索引
                                    
                                    # 創建水印
                                    watermark_file = os.path.join(tmpdirname, "watermark.pdf")
                                    
                                    if watermark_type == "文字水印":
                                        # 創建文字水印
                                        create_text_watermark(
                                            watermark_file, 
                                            watermark_text, 
                                            font_size, 
                                            text_color, 
                                            angle, 
                                            x_gap, 
                                            y_gap,
                                            selected_font  # 傳遞選擇的字體
                                        )
                                    else:
                                        # 創建圖片水印
                                        image_path = os.path.join(tmpdirname, "watermark_image")
                                        with open(image_path, "wb") as f:
                                            f.write(uploaded_image.getbuffer())
                                        
                                        create_image_watermark(
                                            watermark_file,
                                            image_path,
                                            opacity,
                                            size,
                                            position
                                        )
                                    
                                    # 應用水印
                                    output_file = os.path.join(tmpdirname, f"watermarked_{uploaded_file.name}")
                                    add_watermark_to_pdf(temp_file, watermark_file, output_file, pages_to_watermark, password)
                                    
                                    # 提供下載
                                    with open(output_file, "rb") as f:
                                        pdf_bytes = f.read()
                                    
                                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="watermarked_{uploaded_file.name}" class="download-button">下載添加水印的PDF</a>'
                                    st.markdown(href, unsafe_allow_html=True)
                                    
                                    # 成功消息
                                    if len(pages_to_watermark) == total_pages:
                                        st.success(f"已成功為所有 {total_pages} 頁添加水印！")
                                    else:
                                        st.success(f"已成功為 {len(pages_to_watermark)} 頁添加水印！")
                                
                                except Exception as e:
                                    st.error(f"添加水印時出錯: {str(e)}")
                
                except Exception as e:
                    st.error(f"讀取PDF時出錯: {str(e)}")
            else:
                # 如果文件是加密的，提示用戶輸入密碼
                if is_encrypted and not password:
                    st.warning("請輸入PDF密碼以繼續處理")
                elif is_encrypted:
                    st.error("密碼不正確，無法解密PDF文件")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件進行水印添加")
        
        st.markdown("""
        ### 使用說明
        1. 上傳PDF文件
        2. 如果PDF已加密，請輸入密碼解密
        3. 選擇水印類型（文字或圖片）
        4. 設置水印參數：
          - 文字水印：輸入文字、選擇大小、顏色、角度等
          - 圖片水印：上傳圖片、調整透明度、大小和位置
        5. 選擇要應用水印的頁面
        6. 點擊"應用水印"按鈕
        7. 下載處理後的文件
        
        ### 適用場景
        - 添加版權信息或商標
        - 標記文檔的機密性
        - 防止文檔被未經授權複製
        - 添加公司標誌或品牌元素
        - 標示文檔的狀態（如"草稿"、"待審核"等）
        """)

# 創建文字水印
def create_text_watermark(output_file, text, font_size, color, angle, x_gap, y_gap, font_name="Helvetica"):
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    
    # 設置透明度和顏色
    r, g, b, alpha = color
    c.setFillColorRGB(r, g, b, alpha=alpha)
    
    # 設置字體和大小
    c.setFont(font_name, font_size)
    
    # 在整個頁面上重複添加文字
    for y in range(0, int(height), y_gap):
        for x in range(0, int(width), x_gap):
            c.saveState()
            c.translate(x, y)
            c.rotate(angle)
            c.drawString(0, 0, text)
            c.restoreState()
    
    c.save()

# 創建圖片水印
def create_image_watermark(output_file, image_path, opacity, size_percent, position):
    c = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    
    # 加載圖片並計算大小
    img = Image.open(image_path)
    img_width, img_height = img.size
    
    # 計算水印大小（根據頁面寬度的百分比）
    new_width = width * size_percent / 100
    new_height = img_height * (new_width / img_width)
    
    # 計算位置
    if position == "居中":
        x = (width - new_width) / 2
        y = (height - new_height) / 2
    elif position == "左上角":
        x = 20
        y = height - new_height - 20
    elif position == "右上角":
        x = width - new_width - 20
        y = height - new_height - 20
    elif position == "左下角":
        x = 20
        y = 20
    else:  # 右下角
        x = width - new_width - 20
        y = 20
    
    # 繪製圖片
    c.drawImage(image_path, x, y, width=new_width, height=new_height, mask='auto', alpha=opacity)
    c.save()

# 將水印應用到PDF
def add_watermark_to_pdf(input_pdf, watermark_pdf, output_pdf, pages_to_watermark, password=None):
    # 讀取輸入PDF
    reader = PdfReader(input_pdf)
    
    # 如果文件已加密且提供了密碼，嘗試解密
    if reader.is_encrypted and password:
        reader.decrypt(password)
        
    watermark = PdfReader(watermark_pdf)
    watermark_page = watermark.pages[0]
    
    # 創建輸出PDF
    writer = PdfWriter()
    
    # 處理每一頁
    for i, page in enumerate(reader.pages):
        if i in pages_to_watermark:
            # 將水印疊加到頁面上
            page.merge_page(watermark_page)
        writer.add_page(page)
    
    # 保存輸出PDF
    with open(output_pdf, "wb") as f:
        writer.write(f) 