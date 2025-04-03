import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
import base64
from io import BytesIO

def pdf_rotate_page():
    st.header("🔄 PDF旋轉")
    st.write("旋轉PDF文件的頁面方向")
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 保存上傳的文件
            temp_file = os.path.join(tmpdirname, uploaded_file.name)
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 讀取PDF
            pdf = PdfReader(temp_file)
            total_pages = len(pdf.pages)
            
            st.write(f"文件名: {uploaded_file.name}")
            st.write(f"總頁數: {total_pages}")
            
            # 選擇旋轉類型
            st.subheader("選擇旋轉方式")
            rotation_type = st.radio(
                "旋轉方式",
                ["旋轉所有頁面", "旋轉特定頁面"]
            )
            
            # 旋轉角度選擇
            rotation_angle = st.select_slider(
                "旋轉角度",
                options=[0, 90, 180, 270],
                value=90
            )
            
            # 旋轉所有頁面
            if rotation_type == "旋轉所有頁面":
                if st.button("旋轉PDF"):
                    with st.spinner("正在旋轉PDF..."):
                        writer = PdfWriter()
                        
                        # 旋轉每一頁
                        for page in pdf.pages:
                            page.rotate(rotation_angle)
                            writer.add_page(page)
                            
                        # 保存旋轉後的PDF
                        output_file = os.path.join(tmpdirname, f"rotated_{uploaded_file.name}")
                        with open(output_file, "wb") as f:
                            writer.write(f)
                            
                        # 提供下載
                        with open(output_file, "rb") as f:
                            pdf_bytes = f.read()
                            
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="rotated_{uploaded_file.name}" class="download-button">下載旋轉後的PDF</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                        st.success(f"已成功旋轉所有 {total_pages} 頁")
                        
            # 旋轉特定頁面
            else:
                st.write("指定要旋轉的頁面（例如：1-5,7,9-12）")
                page_ranges = st.text_input("頁數範圍", value="1")
                
                if st.button("旋轉PDF"):
                    try:
                        # 解析頁面範圍
                        pages_to_rotate = set()
                        parts = page_ranges.split(',')
                        for part in parts:
                            if '-' in part:
                                start, end = map(int, part.split('-'))
                                # 檢查範圍是否有效
                                if start < 1 or end > total_pages or start > end:
                                    st.error(f"無效的頁數範圍: {part}")
                                    break
                                pages_to_rotate.update(range(start, end + 1))
                            else:
                                page = int(part)
                                if page < 1 or page > total_pages:
                                    st.error(f"無效的頁數: {part}")
                                    break
                                pages_to_rotate.add(page)
                        
                        # 執行旋轉
                        with st.spinner("正在旋轉PDF..."):
                            writer = PdfWriter()
                            
                            # 處理每一頁
                            for i, page in enumerate(pdf.pages, 1):
                                if i in pages_to_rotate:
                                    page.rotate(rotation_angle)
                                writer.add_page(page)
                                
                            # 保存旋轉後的PDF
                            output_file = os.path.join(tmpdirname, f"rotated_{uploaded_file.name}")
                            with open(output_file, "wb") as f:
                                writer.write(f)
                                
                            # 提供下載
                            with open(output_file, "rb") as f:
                                pdf_bytes = f.read()
                                
                            b64_pdf = base64.b64encode(pdf_bytes).decode()
                            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="rotated_{uploaded_file.name}" class="download-button">下載旋轉後的PDF</a>'
                            st.markdown(href, unsafe_allow_html=True)
                            
                            st.success(f"已成功旋轉 {len(pages_to_rotate)} 頁")
                            
                    except Exception as e:
                        st.error(f"處理過程中出錯: {str(e)}")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件進行旋轉操作")
        
        st.markdown("""
        ### 使用說明
        1. 上傳您要旋轉的PDF文件
        2. 選擇旋轉方式：
           - 旋轉所有頁面
           - 旋轉特定頁面（如1-5,7,10等）
        3. 選擇旋轉角度（90°、180°或270°）
        4. 點擊"旋轉PDF"按鈕
        5. 下載處理後的文件
        
        ### 適用場景
        - 修正掃描文檔的方向
        - 將橫向頁面變為縱向，或反之
        - 調整文檔中特定頁面的閱讀方向
        """) 