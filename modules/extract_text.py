import streamlit as st
import os
import tempfile
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer
import base64
from io import BytesIO

def pdf_extract_text_page():
    st.header("📝 PDF文字提取")
    st.write("從PDF文件中提取文本內容")
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 處理文件名以確保合法
            safe_filename = "".join([c for c in uploaded_file.name if c.isalnum() or c in "._- "]).strip()
            if not safe_filename:
                safe_filename = "uploaded_file.pdf"
            elif not safe_filename.lower().endswith('.pdf'):
                safe_filename += '.pdf'
            
            # 獲取安全的基本文件名（不包含擴展名）
            safe_basename = os.path.splitext(safe_filename)[0]
            
            # 保存上傳的文件
            temp_file = os.path.join(tmpdirname, safe_filename)
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 選擇提取模式
            st.subheader("選擇提取模式")
            extraction_mode = st.radio(
                "提取模式",
                ["提取所有文本", "提取特定頁面", "提取表格數據(試驗性)"]
            )
            
            # 提供檢測OCR選項
            use_ocr = st.checkbox("使用OCR識別掃描文檔中的文字（需要Tesseract）", value=False)
            
            if extraction_mode == "提取所有文本":
                if st.button("提取文本"):
                    with st.spinner("正在提取文本..."):
                        try:
                            if use_ocr:
                                st.warning("OCR模式可能需要較長時間，請耐心等待")
                                # 這裡可以集成Tesseract OCR處理，但需要額外的庫
                                # 以下是簡化的OCR處理
                                import pytesseract
                                from pdf2image import convert_from_path
                                
                                # 將PDF轉換為圖像
                                images = convert_from_path(temp_file)
                                
                                # 從圖像中提取文本
                                text = ""
                                for i, image in enumerate(images):
                                    page_text = pytesseract.image_to_string(image, lang='chi_tra+eng')
                                    text += f"===== 第 {i+1} 頁 =====\n{page_text}\n\n"
                            else:
                                # 使用pdfminer提取文本
                                text = extract_text(temp_file)
                                
                            # 顯示提取的文本
                            st.subheader("提取的文本：")
                            st.text_area("", text, height=500)
                            
                            # 創建文本文件下載
                            output_file = os.path.join(tmpdirname, f"{safe_basename}.txt")
                            with open(output_file, "w", encoding="utf-8") as f:
                                f.write(text)
                                
                            with open(output_file, "rb") as f:
                                txt_bytes = f.read()
                                
                            b64_txt = base64.b64encode(txt_bytes).decode()
                            original_basename = os.path.splitext(uploaded_file.name)[0]
                            href = f'<a href="data:text/plain;base64,{b64_txt}" download="{original_basename}.txt" class="download-button">下載文本文件</a>'
                            st.markdown(href, unsafe_allow_html=True)
                            
                            st.success("文本提取完成！")
                        except Exception as e:
                            st.error(f"提取過程中出錯: {str(e)}")
            
            elif extraction_mode == "提取特定頁面":
                # 首先獲取總頁數
                try:
                    from PyPDF2 import PdfReader
                    pdf = PdfReader(temp_file)
                    total_pages = len(pdf.pages)
                    
                    st.write(f"總頁數: {total_pages}")
                    
                    # 頁面選擇
                    page_ranges = st.text_input(
                        "指定頁數範圍（例如：1-5,7,9-12）",
                        value="1"
                    )
                    
                    if st.button("提取文本"):
                        with st.spinner("正在提取文本..."):
                            try:
                                # 解析頁面範圍
                                pages_to_extract = []
                                parts = page_ranges.split(',')
                                for part in parts:
                                    if '-' in part:
                                        start, end = map(int, part.split('-'))
                                        # 檢查範圍是否有效
                                        if start < 1 or end > total_pages or start > end:
                                            st.error(f"無效的頁數範圍: {part}")
                                            break
                                        pages_to_extract.extend(range(start, end + 1))
                                    else:
                                        page = int(part)
                                        if page < 1 or page > total_pages:
                                            st.error(f"無效的頁數: {part}")
                                            break
                                        pages_to_extract.append(page)
                                
                                # 提取特定頁面的文本
                                if use_ocr:
                                    st.warning("OCR模式可能需要較長時間，請耐心等待")
                                    import pytesseract
                                    from pdf2image import convert_from_path
                                    
                                    # 將PDF轉換為圖像
                                    images = convert_from_path(temp_file, first_page=min(pages_to_extract), last_page=max(pages_to_extract))
                                    
                                    # 從圖像中提取文本
                                    text = ""
                                    for i, image in enumerate(images):
                                        page_num = pages_to_extract[i] if i < len(pages_to_extract) else i + min(pages_to_extract)
                                        page_text = pytesseract.image_to_string(image, lang='chi_tra+eng')
                                        text += f"===== 第 {page_num} 頁 =====\n{page_text}\n\n"
                                else:
                                    # 使用pdfminer提取特定頁面文本
                                    text = ""
                                    for page_layout in extract_pages(temp_file):
                                        page_num = page_layout.pageid + 1  # 頁碼從1開始
                                        if page_num in pages_to_extract:
                                            page_text = ""
                                            for element in page_layout:
                                                if isinstance(element, LTTextContainer):
                                                    page_text += element.get_text()
                                            text += f"===== 第 {page_num} 頁 =====\n{page_text}\n\n"
                                
                                # 顯示提取的文本
                                st.subheader("提取的文本：")
                                st.text_area("", text, height=500)
                                
                                # 創建文本文件下載
                                output_file = os.path.join(tmpdirname, f"{safe_basename}_selected_pages.txt")
                                with open(output_file, "w", encoding="utf-8") as f:
                                    f.write(text)
                                    
                                with open(output_file, "rb") as f:
                                    txt_bytes = f.read()
                                    
                                b64_txt = base64.b64encode(txt_bytes).decode()
                                original_basename = os.path.splitext(uploaded_file.name)[0]
                                href = f'<a href="data:text/plain;base64,{b64_txt}" download="{original_basename}_selected_pages.txt" class="download-button">下載文本文件</a>'
                                st.markdown(href, unsafe_allow_html=True)
                                
                                st.success("選定頁面的文本提取完成！")
                            except Exception as e:
                                st.error(f"提取過程中出錯: {str(e)}")
                
                except Exception as e:
                    st.error(f"讀取PDF頁數時出錯: {str(e)}")
            
            elif extraction_mode == "提取表格數據(試驗性)":
                st.warning("表格提取功能為試驗性功能，可能無法準確識別所有表格")
                
                output_format = st.radio(
                    "輸出格式",
                    ["CSV", "Excel"]
                )
                
                if st.button("提取表格"):
                    with st.spinner("正在提取表格數據..."):
                        try:
                            # 使用tabula-py提取表格
                            import tabula
                            
                            # 提取表格
                            tables = tabula.read_pdf(temp_file, pages='all', multiple_tables=True)
                            
                            if len(tables) > 0:
                                # 顯示提取的表格
                                st.subheader(f"共提取到 {len(tables)} 個表格：")
                                
                                for i, table in enumerate(tables):
                                    st.write(f"表格 {i+1}:")
                                    st.dataframe(table)
                                
                                # 根據選擇的格式創建下載
                                if output_format == "CSV":
                                    # 創建一個ZIP文件包含所有CSV
                                    csv_dir = os.path.join(tmpdirname, "csv_tables")
                                    os.makedirs(csv_dir, exist_ok=True)
                                    
                                    csv_files = []
                                    for i, table in enumerate(tables):
                                        csv_file = os.path.join(csv_dir, f"table_{i+1}.csv")
                                        table.to_csv(csv_file, index=False)
                                        csv_files.append(csv_file)
                                    
                                    # 創建ZIP
                                    import zipfile
                                    zip_file = os.path.join(tmpdirname, "tables.zip")
                                    with zipfile.ZipFile(zip_file, 'w') as zipf:
                                        for file in csv_files:
                                            zipf.write(file, os.path.basename(file))
                                    
                                    # 提供ZIP下載
                                    with open(zip_file, "rb") as f:
                                        zip_bytes = f.read()
                                    
                                    b64_zip = base64.b64encode(zip_bytes).decode()
                                    href = f'<a href="data:application/zip;base64,{b64_zip}" download="tables.zip" class="download-button">下載CSV表格</a>'
                                    st.markdown(href, unsafe_allow_html=True)
                                
                                else:  # Excel
                                    # 將所有表格保存到一個Excel文件的不同工作表
                                    excel_file = os.path.join(tmpdirname, "tables.xlsx")
                                    
                                    import pandas as pd
                                    with pd.ExcelWriter(excel_file) as writer:
                                        for i, table in enumerate(tables):
                                            table.to_excel(writer, sheet_name=f"表格_{i+1}", index=False)
                                    
                                    # 提供Excel下載
                                    with open(excel_file, "rb") as f:
                                        excel_bytes = f.read()
                                    
                                    b64_excel = base64.b64encode(excel_bytes).decode()
                                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_excel}" download="tables.xlsx" class="download-button">下載Excel表格</a>'
                                    st.markdown(href, unsafe_allow_html=True)
                                
                                st.success("表格提取完成！")
                            else:
                                st.info("未檢測到表格，請確認PDF中是否包含表格數據")
                                
                        except Exception as e:
                            st.error(f"提取表格過程中出錯: {str(e)}")
                            st.info("提示：表格提取需要安裝額外的依賴：pip install tabula-py pandas openpyxl")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件進行文本提取")
        
        st.markdown("""
        ### 使用說明
        1. 上傳您的PDF文件
        2. 選擇提取模式：
           - 提取所有文本：從整個文件中提取
           - 提取特定頁面：只從選定頁面提取
           - 提取表格數據：嘗試識別和提取表格(試驗性功能)
        3. 對於掃描的文檔，可啟用OCR功能
        4. 點擊相應的提取按鈕
        5. 下載提取的結果
        
        ### 適用場景
        - 從PDF報告中提取文字進行分析
        - 獲取掃描文檔中的文字內容
        - 提取PDF中的表格數據進行處理
        """) 