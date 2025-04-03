import streamlit as st
import os
import tempfile
from PyPDF2 import PdfMerger, PdfReader
import base64
from io import BytesIO

def pdf_merge_page():
    st.header("📄 PDF合併")
    st.write("將多個PDF文件合併為一個PDF文件")
    
    # 文件上傳區域
    uploaded_files = st.file_uploader(
        "選擇多個PDF文件（可多選）", 
        type="pdf", 
        accept_multiple_files=True
    )
    
    # 如果用戶上傳了文件
    if uploaded_files:
        # 顯示上傳的文件
        st.write(f"已上傳 {len(uploaded_files)} 個文件:")
        file_names = [file.name for file in uploaded_files]
        
        # 檢查是否有加密的PDF文件
        encrypted_files = []
        with tempfile.TemporaryDirectory() as check_tmpdirname:
            for i, file in enumerate(uploaded_files):
                temp_check_file = os.path.join(check_tmpdirname, f"check_{i}.pdf")
                with open(temp_check_file, "wb") as f:
                    f.write(file.getbuffer())
                
                # 檢查文件是否加密
                try:
                    reader = PdfReader(temp_check_file)
                    if reader.is_encrypted:
                        encrypted_files.append((i, file.name))
                except Exception as e:
                    if "encrypted" in str(e).lower():
                        encrypted_files.append((i, file.name))
        
        # 如果有加密文件，顯示密碼輸入區域
        file_passwords = {}
        if encrypted_files:
            st.warning(f"檢測到 {len(encrypted_files)} 個加密的PDF文件。請提供密碼解鎖:")
            
            with st.expander("加密文件處理", expanded=True):
                for idx, filename in encrypted_files:
                    password_key = f"password_{idx}"
                    st.text(f"文件: {filename}")
                    file_passwords[idx] = st.text_input(
                        f"輸入 '{filename}' 的密碼", 
                        type="password",
                        key=password_key
                    )
        
        # 顯示文件列表並允許排序
        with st.expander("查看並排序文件", expanded=True):
            for i, name in enumerate(file_names):
                is_encrypted = any(idx == i for idx, _ in encrypted_files)
                st.text(f"{i+1}. {name} {'🔒' if is_encrypted else ''}")
                
            # 允許用戶重新排序文件
            st.write("通過以逗號分隔的數字排序文件（例如：2,1,3）")
            order_input = st.text_input("重新排序（留空保持原始順序）")
            
            if order_input:
                try:
                    # 解析用戶輸入的順序
                    new_order = [int(x.strip())-1 for x in order_input.split(',')]
                    
                    # 檢查順序是否有效
                    if set(new_order) != set(range(len(uploaded_files))):
                        st.error("排序無效，請確保包含所有文件編號")
                    else:
                        # 重新排序文件列表
                        uploaded_files = [uploaded_files[i] for i in new_order]
                        
                        # 同時更新加密文件索引
                        new_encrypted_files = []
                        for old_idx, name in encrypted_files:
                            new_idx = new_order.index(old_idx)
                            new_encrypted_files.append((new_idx, name))
                            # 更新密碼字典中的索引
                            if old_idx in file_passwords:
                                file_passwords[new_idx] = file_passwords.pop(old_idx)
                        
                        encrypted_files = new_encrypted_files
                        st.success("文件已重新排序")
                        
                        # 顯示新順序
                        st.write("新的文件順序:")
                        for i, file in enumerate(uploaded_files):
                            is_encrypted = any(idx == i for idx, _ in encrypted_files)
                            st.text(f"{i+1}. {file.name} {'🔒' if is_encrypted else ''}")
                except:
                    st.error("排序格式無效，請使用逗號分隔的數字")

        # 輸出文件名
        output_name = st.text_input("輸出文件名", value="merged_document.pdf")
        if not output_name.endswith('.pdf'):
            output_name += '.pdf'
            
        # 處理輸出文件名以確保合法
        safe_output_name = "".join([c for c in output_name if c.isalnum() or c in "._- "]).strip()
        if not safe_output_name:
            safe_output_name = "merged_document.pdf"
        elif not safe_output_name.lower().endswith('.pdf'):
            safe_output_name += '.pdf'
        
        # 合併按鈕
        if st.button("合併PDF文件"):
            if len(uploaded_files) > 1:
                # 檢查是否所有加密文件都有提供密碼
                missing_passwords = [name for idx, name in encrypted_files if not file_passwords.get(idx)]
                if missing_passwords:
                    st.error(f"請為所有加密文件提供密碼。以下文件缺少密碼: {', '.join(missing_passwords)}")
                else:
                    with st.spinner("正在合併PDF文件..."):
                        # 使用臨時目錄保存上傳的文件
                        with tempfile.TemporaryDirectory() as tmpdirname:
                            # 保存上傳的文件到臨時目錄並處理加密文件
                            temp_files = []
                            error_files = []
                            
                            for i, file in enumerate(uploaded_files):
                                temp_file = os.path.join(tmpdirname, f"file_{i}.pdf")
                                with open(temp_file, "wb") as f:
                                    f.write(file.getbuffer())
                                
                                # 檢查是否為加密文件，如果是則嘗試解密
                                is_encrypted_idx = next((idx for idx, _ in encrypted_files if idx == i), None)
                                if is_encrypted_idx is not None:
                                    password = file_passwords.get(i)
                                    decrypted_file = os.path.join(tmpdirname, f"decrypted_{i}.pdf")
                                    
                                    try:
                                        # 嘗試解密文件
                                        reader = PdfReader(temp_file)
                                        writer = PdfMerger()
                                        
                                        # 使用密碼解密
                                        if reader.is_encrypted:
                                            decrypt_success = False
                                            
                                            # 嘗試標準解密
                                            try:
                                                decrypt_result = reader.decrypt(password)
                                                if decrypt_result > 0:
                                                    decrypt_success = True
                                            except Exception:
                                                pass
                                            
                                            # 如果標準解密失敗，嘗試其他編碼
                                            if not decrypt_success:
                                                for encoding in ['utf-8', 'latin1', 'cp1252', 'gbk', 'big5']:
                                                    try:
                                                        reader = PdfReader(temp_file)
                                                        if reader.decrypt(password) > 0:
                                                            decrypt_success = True
                                                            break
                                                    except Exception:
                                                        continue
                                            
                                            # 嘗試使用pikepdf
                                            if not decrypt_success:
                                                try:
                                                    import pikepdf
                                                    pdf = pikepdf.open(temp_file, password=password)
                                                    pdf.save(decrypted_file)
                                                    temp_file = decrypted_file
                                                    decrypt_success = True
                                                except Exception:
                                                    pass
                                            
                                            # 如果所有方法都失敗
                                            if not decrypt_success:
                                                error_files.append(file.name)
                                                continue
                                    except Exception as e:
                                        error_files.append(file.name)
                                        continue
                                
                                temp_files.append(temp_file)
                            
                            # 如果有無法解密的文件，顯示錯誤並中斷操作
                            if error_files:
                                st.error(f"無法解密以下文件，請檢查密碼是否正確: {', '.join(error_files)}")
                            else:
                                try:
                                    # 創建合併器對象
                                    merger = PdfMerger()
                                    
                                    # 添加所有PDF文件
                                    for temp_file in temp_files:
                                        merger.append(temp_file)
                                    
                                    # 保存合併後的PDF
                                    merged_file = os.path.join(tmpdirname, safe_output_name)
                                    merger.write(merged_file)
                                    merger.close()
                                    
                                    # 讀取合併後的文件
                                    with open(merged_file, "rb") as f:
                                        pdf_bytes = f.read()
                                    
                                    # 創建下載按鈕
                                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{output_name}" class="download-button">下載合併後的PDF</a>'
                                    st.markdown(href, unsafe_allow_html=True)
                                    
                                    # 顯示成功消息
                                    if encrypted_files:
                                        st.success(f"已成功解密和合併 {len(uploaded_files)} 個PDF文件")
                                    else:
                                        st.success(f"已成功合併 {len(uploaded_files)} 個PDF文件")
                                except Exception as e:
                                    st.error(f"合併過程中出錯: {str(e)}")
            else:
                st.error("請至少上傳2個PDF文件進行合併")
    else:
        # 顯示使用說明
        st.info("請先上傳至少2個PDF文件進行合併操作")
        
        # 示例
        st.markdown("""
        ### 使用說明
        1. 點擊上方"選擇多個PDF文件"按鈕上傳多個PDF
        2. 若上傳了加密PDF文件，系統會請您提供密碼
        3. 可以通過排序功能調整PDF合併順序
        4. 設置輸出文件名稱
        5. 點擊"合併PDF文件"按鈕進行合併
        6. 完成後下載合併後的文件
        
        ### 適用場景
        - 合併多個報告為一個文檔
        - 將分散的章節合併為完整書籍
        - 整合多個表格為完整報表
        - 處理並合併受密碼保護的PDF文件
        """) 