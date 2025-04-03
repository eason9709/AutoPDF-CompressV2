import streamlit as st
import os
import tempfile
import zipfile
from PyPDF2 import PdfReader, PdfWriter
import base64
from io import BytesIO

def pdf_split_page():
    st.header("✂️ PDF分割")
    st.write("將PDF文件分割為多個單獨的文件")
    
    # 文件上傳區域
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 處理文件名以確保合法
            safe_filename = "".join([c for c in uploaded_file.name if c.isalnum() or c in "._- "]).strip()
            if not safe_filename:
                safe_filename = "uploaded_file.pdf"
            elif not safe_filename.lower().endswith('.pdf'):
                safe_filename += '.pdf'
                
            # 保存上傳的文件
            temp_file = os.path.join(tmpdirname, safe_filename)
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 先檢查文件是否加密
            try:
                pdf = PdfReader(temp_file)
                is_encrypted = pdf.is_encrypted
            except Exception as e:
                is_encrypted = "encrypted" in str(e).lower()
            
            # 如果文件已加密，顯示密碼輸入框
            password = None
            if is_encrypted:
                st.warning("檢測到加密的PDF文件，請提供密碼進行解密。")
                password = st.text_input("輸入PDF密碼", type="password")
                
                if password:
                    try:
                        # 嘗試使用提供的密碼解密
                        pdf = PdfReader(temp_file)
                        decrypt_success = False
                        
                        # 標準解密嘗試
                        try:
                            decrypt_result = pdf.decrypt(password)
                            if decrypt_result > 0:
                                decrypt_success = True
                                is_encrypted = False
                                st.success("PDF文件解密成功！")
                        except Exception:
                            pass
                        
                        # 如果標準解密失敗，嘗試其他編碼
                        if not decrypt_success:
                            for encoding in ['utf-8', 'latin1', 'cp1252', 'gbk', 'big5']:
                                try:
                                    pdf = PdfReader(temp_file)
                                    if pdf.decrypt(password) > 0:
                                        decrypt_success = True
                                        is_encrypted = False
                                        st.success(f"使用 {encoding} 編碼成功解密！")
                                        break
                                except Exception:
                                    continue
                        
                        # 如果以上方法都失敗，嘗試使用pikepdf
                        if not decrypt_success:
                            try:
                                import pikepdf
                                decrypted_file = os.path.join(tmpdirname, "decrypted_file.pdf")
                                pdf_pikepdf = pikepdf.open(temp_file, password=password)
                                pdf_pikepdf.save(decrypted_file)
                                temp_file = decrypted_file
                                pdf = PdfReader(temp_file)
                                is_encrypted = False
                                st.success("使用增強方法成功解密！")
                            except Exception as e:
                                st.error(f"解密失敗: {str(e)}")
                                st.info("請確認密碼是否正確")
                    except Exception as e:
                        st.error(f"解密過程中出錯: {str(e)}")
            
            # 讀取PDF
            if not is_encrypted:
                try:
                    if 'pdf' not in locals() or pdf is None:
                        pdf = PdfReader(temp_file)
                    
                    total_pages = len(pdf.pages)
                    
                    st.write(f"文件名: {uploaded_file.name}")
                    st.write(f"總頁數: {total_pages}")
                    
                    # 分割選項
                    st.subheader("選擇分割方式")
                    split_option = st.radio(
                        "分割方式",
                        ["按頁數範圍分割", "每X頁分割為一個文件", "每頁分割為單獨文件"]
                    )
                    
                    # 按頁數範圍分割
                    if split_option == "按頁數範圍分割":
                        st.write("指定頁數範圍（例如：1-5,7,9-12）")
                        page_ranges = st.text_input("頁數範圍", value="1-5")
                        
                        if st.button("分割PDF"):
                            try:
                                ranges = []
                                # 解析頁數範圍
                                parts = page_ranges.split(',')
                                for part in parts:
                                    if '-' in part:
                                        start, end = map(int, part.split('-'))
                                        # 檢查範圍是否有效
                                        if start < 1 or end > total_pages or start > end:
                                            st.error(f"無效的頁數範圍: {part}")
                                            break
                                        ranges.append((start-1, end-1))  # 轉換為0-索引
                                    else:
                                        page = int(part)
                                        if page < 1 or page > total_pages:
                                            st.error(f"無效的頁數: {part}")
                                            break
                                        ranges.append((page-1, page-1))  # 轉換為0-索引
                                
                                # 執行分割
                                with st.spinner("正在分割PDF..."):
                                    # 創建分割文件目錄
                                    split_dir = os.path.join(tmpdirname, "split")
                                    os.makedirs(split_dir, exist_ok=True)
                                    
                                    # 對每個範圍創建一個新的PDF
                                    output_files = []
                                    for i, (start, end) in enumerate(ranges):
                                        output = PdfWriter()
                                        for page_num in range(start, end + 1):
                                            output.add_page(pdf.pages[page_num])
                                        
                                        output_file = os.path.join(split_dir, f"split_{i+1}.pdf")
                                        with open(output_file, "wb") as f:
                                            output.write(f)
                                        output_files.append(output_file)
                                    
                                    # 創建ZIP文件
                                    zip_file = os.path.join(tmpdirname, "split_files.zip")
                                    with zipfile.ZipFile(zip_file, 'w') as zipf:
                                        for file in output_files:
                                            zipf.write(file, os.path.basename(file))
                                    
                                    # 提供下載
                                    with open(zip_file, "rb") as f:
                                        zip_bytes = f.read()
                                    
                                    b64_zip = base64.b64encode(zip_bytes).decode()
                                    href = f'<a href="data:application/zip;base64,{b64_zip}" download="split_files.zip" class="download-button">下載分割後的PDF文件</a>'
                                    st.markdown(href, unsafe_allow_html=True)
                                    
                                    st.success(f"成功創建 {len(output_files)} 個分割文件")
                            except Exception as e:
                                st.error(f"處理過程中出錯: {str(e)}")
                    
                    # 每X頁分割為一個文件
                    elif split_option == "每X頁分割為一個文件":
                        pages_per_doc = st.number_input("每個文件的頁數", min_value=1, max_value=total_pages, value=1)
                        
                        if st.button("分割PDF"):
                            with st.spinner("正在分割PDF..."):
                                # 創建分割文件目錄
                                split_dir = os.path.join(tmpdirname, "split")
                                os.makedirs(split_dir, exist_ok=True)
                                
                                # 計算需要創建的文件數
                                num_output_files = (total_pages + pages_per_doc - 1) // pages_per_doc
                                
                                # 分割PDF
                                output_files = []
                                for i in range(num_output_files):
                                    output = PdfWriter()
                                    start_page = i * pages_per_doc
                                    end_page = min(start_page + pages_per_doc, total_pages)
                                    
                                    for page_num in range(start_page, end_page):
                                        output.add_page(pdf.pages[page_num])
                                    
                                    output_file = os.path.join(split_dir, f"split_{i+1}.pdf")
                                    with open(output_file, "wb") as f:
                                        output.write(f)
                                    output_files.append(output_file)
                                
                                # 創建ZIP文件
                                zip_file = os.path.join(tmpdirname, "split_files.zip")
                                with zipfile.ZipFile(zip_file, 'w') as zipf:
                                    for file in output_files:
                                        zipf.write(file, os.path.basename(file))
                                
                                # 提供下載
                                with open(zip_file, "rb") as f:
                                    zip_bytes = f.read()
                                
                                b64_zip = base64.b64encode(zip_bytes).decode()
                                href = f'<a href="data:application/zip;base64,{b64_zip}" download="split_files.zip" class="download-button">下載分割後的PDF文件</a>'
                                st.markdown(href, unsafe_allow_html=True)
                                
                                st.success(f"成功創建 {len(output_files)} 個分割文件")
                    
                    # 每頁分割為單獨文件
                    else:  # "每頁分割為單獨文件"
                        if st.button("分割PDF"):
                            with st.spinner("正在分割PDF..."):
                                # 創建分割文件目錄
                                split_dir = os.path.join(tmpdirname, "split")
                                os.makedirs(split_dir, exist_ok=True)
                                
                                # 分割PDF，每頁一個文件
                                output_files = []
                                for page_num in range(total_pages):
                                    output = PdfWriter()
                                    output.add_page(pdf.pages[page_num])
                                    
                                    output_file = os.path.join(split_dir, f"page_{page_num+1}.pdf")
                                    with open(output_file, "wb") as f:
                                        output.write(f)
                                    output_files.append(output_file)
                                
                                # 創建ZIP文件
                                zip_file = os.path.join(tmpdirname, "split_files.zip")
                                with zipfile.ZipFile(zip_file, 'w') as zipf:
                                    for file in output_files:
                                        zipf.write(file, os.path.basename(file))
                                
                                # 提供下載
                                with open(zip_file, "rb") as f:
                                    zip_bytes = f.read()
                                
                                b64_zip = base64.b64encode(zip_bytes).decode()
                                href = f'<a href="data:application/zip;base64,{b64_zip}" download="split_files.zip" class="download-button">下載分割後的PDF文件</a>'
                                st.markdown(href, unsafe_allow_html=True)
                                
                                st.success(f"成功將PDF分割為 {total_pages} 個單頁文件")
                except Exception as e:
                    st.error(f"讀取PDF時出錯: {str(e)}")
            else:
                # 如果文件仍然加密，提醒用戶
                if not password:
                    st.info("請輸入密碼解密PDF後進行分割操作")
                else:
                    st.error("密碼不正確，無法解密PDF文件")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件進行分割操作")
        
        st.markdown("""
        ### 使用說明
        1. 上傳您要分割的PDF文件
        2. 如果PDF已加密，請提供密碼解密
        3. 選擇以下分割方式之一：
           - 按頁數範圍分割（例如：1-5,7,9-12）
           - 每X頁分割為一個文件
           - 每頁分割為單獨文件
        4. 點擊"分割PDF"按鈕
        5. 下載包含所有分割文件的ZIP壓縮包
        
        ### 適用場景
        - 提取PDF中的特定章節或頁面
        - 將大型PDF文檔拆分為更小的部分
        - 從加密PDF中提取內容（需要密碼）
        """) 