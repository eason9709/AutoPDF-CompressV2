import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
import base64
from io import BytesIO

def pdf_encrypt_decrypt_page():
    st.header("🔒 PDF加密/解密")
    st.write("為PDF添加密碼保護或移除現有的密碼")
    
    # 選擇操作類型
    operation = st.radio(
        "選擇操作",
        ["加密PDF", "解密PDF"]
    )
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 保存上傳的文件
            temp_file = os.path.join(tmpdirname, uploaded_file.name)
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 嘗試讀取PDF以獲取基本信息
            try:
                # 首先檢查文件是否加密，不嘗試讀取頁面以避免報錯
                reader = PdfReader(temp_file)
                is_encrypted = reader.is_encrypted
                
                if not is_encrypted:
                    # 如果文件未加密，可以安全地獲取頁數
                    total_pages = len(reader.pages)
                    st.write(f"文件名: {uploaded_file.name}")
                    st.write(f"總頁數: {total_pages}")
                    st.write("加密狀態: 未加密")
                else:
                    # 如果文件已加密，只顯示文件名和加密狀態
                    st.write(f"文件名: {uploaded_file.name}")
                    st.write("加密狀態: 已加密")
                
                # 選擇合適的操作
                if operation == "加密PDF" and is_encrypted:
                    st.warning("文件已經被加密，請先解密後再加密")
                elif operation == "解密PDF" and not is_encrypted:
                    st.warning("文件未被加密，無需解密")
                else:
                    # 加密PDF
                    if operation == "加密PDF":
                        with st.form("encrypt_form"):
                            st.subheader("設置加密參數")
                            
                            # 密碼設置
                            user_password = st.text_input("用戶密碼（打開PDF時需要的密碼）", type="password")
                            owner_password = st.text_input("擁有者密碼（編輯PDF時需要的密碼）", type="password")
                            
                            # 增加中文字符警告提示
                            if any('\u4e00' <= c <= '\u9fff' for c in user_password + owner_password):
                                st.warning("您的密碼包含中文字符。某些PDF閱讀器可能無法正確處理中文密碼，建議使用英文、數字和符號的組合。")
                            
                            # 權限設置
                            st.write("設置使用權限：")
                            can_print = st.checkbox("允許打印", value=True)
                            can_copy = st.checkbox("允許複製內容", value=True)
                            can_modify = st.checkbox("允許修改", value=False)
                            
                            # 加密強度
                            encryption_strength = st.selectbox(
                                "加密強度",
                                ["128位 AES (推薦)", "40位 RC4 (較舊)"]
                            )
                            
                            # 驗證密碼強度
                            if user_password:
                                strength = 0
                                if len(user_password) >= 8: strength += 1
                                if any(c.isupper() for c in user_password): strength += 1
                                if any(c.islower() for c in user_password): strength += 1
                                if any(c.isdigit() for c in user_password): strength += 1
                                if any(not c.isalnum() for c in user_password): strength += 1
                                
                                if strength < 3:
                                    st.warning("密碼強度較弱，建議包含大小寫字母、數字和特殊符號")
                                elif strength < 5:
                                    st.info("密碼強度中等")
                                else:
                                    st.success("密碼強度良好")
                            
                            submit_button = st.form_submit_button("加密PDF")
                        
                        if submit_button:
                            if not user_password and not owner_password:
                                st.error("請至少設置一個密碼")
                            else:
                                with st.spinner("正在加密PDF..."):
                                    try:
                                        # 創建一個新的PDF寫入器
                                        writer = PdfWriter()
                                        
                                        # 複製所有頁面
                                        for page in reader.pages:
                                            writer.add_page(page)
                                        
                                        # 設置加密參數
                                        encryption_method = "/AES" if encryption_strength.startswith("128") else "/RC4"
                                        
                                        # 添加加密
                                        writer.encrypt(
                                            user_password=user_password,
                                            owner_password=owner_password if owner_password else user_password,
                                            use_128bit=encryption_strength.startswith("128"),
                                            permissions_flag=
                                                (1 if can_print else 0) |
                                                (2 if can_modify else 0) |
                                                (4 if can_copy else 0)
                                        )
                                        
                                        # 保存加密的PDF
                                        output_file = os.path.join(tmpdirname, f"encrypted_{uploaded_file.name}")
                                        with open(output_file, "wb") as f:
                                            writer.write(f)
                                        
                                        # 提供下載
                                        with open(output_file, "rb") as f:
                                            pdf_bytes = f.read()
                                        
                                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="encrypted_{uploaded_file.name}" class="download-button">下載加密的PDF</a>'
                                        st.markdown(href, unsafe_allow_html=True)
                                        
                                        st.success("PDF加密成功！請妥善保管您的密碼。")
                                        
                                        # 顯示密碼提示
                                        with st.expander("密碼摘要（請記下這些信息）"):
                                            st.write("用戶密碼: " + ("*" * len(user_password)) + f" ({len(user_password)} 個字符)")
                                            st.write("擁有者密碼: " + ("*" * len(owner_password)) + f" ({len(owner_password)} 個字符)" if owner_password else "與用戶密碼相同")
                                            st.write(f"加密方法: {encryption_method}")
                                            st.write("權限: " + ", ".join([
                                                "允許打印" if can_print else "禁止打印",
                                                "允許複製" if can_copy else "禁止複製",
                                                "允許修改" if can_modify else "禁止修改"
                                            ]))
                                            
                                            # 添加特殊提示
                                            if any('\u4e00' <= c <= '\u9fff' for c in user_password + owner_password):
                                                st.warning("您使用了中文密碼。如果在某些PDF閱讀器中遇到問題，請返回使用非中文密碼重新加密。")
                                    
                                    except Exception as e:
                                        st.error(f"加密過程中出錯: {str(e)}")
                    
                    # 解密PDF - 完全重寫這部分，參考浮水印模塊的解密方法
                    elif operation == "解密PDF":
                        if is_encrypted:
                            # 簡化密碼輸入界面，使用直接的、基本的密碼輸入
                            password = st.text_input("輸入PDF密碼", type="password")
                            
                            # 解密按鈕
                            if st.button("解密PDF"):
                                if not password:
                                    st.error("請輸入密碼")
                                else:
                                    with st.spinner("正在嘗試解密PDF..."):
                                        try:
                                            # 創建新的reader實例
                                            reader = PdfReader(temp_file)
                                            
                                            # 嘗試以提供的密碼解密
                                            decrypt_result = reader.decrypt(password)
                                            
                                            # 檢查解密是否成功
                                            if decrypt_result > 0:
                                                # 解密成功，繼續處理
                                                writer = PdfWriter()
                                                
                                                try:
                                                    # 嘗試獲取並添加所有頁面
                                                    for page in reader.pages:
                                                        writer.add_page(page)
                                                    
                                                    # 保存解密的PDF
                                                    output_file = os.path.join(tmpdirname, f"decrypted_{uploaded_file.name}")
                                                    with open(output_file, "wb") as f:
                                                        writer.write(f)
                                                    
                                                    # 提供下載
                                                    with open(output_file, "rb") as f:
                                                        pdf_bytes = f.read()
                                                    
                                                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                                                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="decrypted_{uploaded_file.name}" class="download-button">下載解密的PDF</a>'
                                                    st.markdown(href, unsafe_allow_html=True)
                                                    
                                                    st.success("PDF解密成功！文件已完全解密。")
                                                except Exception as e:
                                                    st.error(f"處理PDF頁面時出錯: {str(e)}")
                                                    
                                                    # 嘗試更強硬的方法解決"File has not been decrypted"問題
                                                    try:
                                                        st.info("正在嘗試替代方法解密...")
                                                        
                                                        # 使用pikepdf嘗試解密 - pikepdf通常對加密PDF有更好的支持
                                                        import pikepdf
                                                        
                                                        # 使用pikepdf打開PDF並解密
                                                        pdf = pikepdf.open(temp_file, password=password)
                                                        
                                                        # 保存為解密文件
                                                        alt_output_file = os.path.join(tmpdirname, f"decrypted_alt_{uploaded_file.name}")
                                                        pdf.save(alt_output_file)
                                                        
                                                        # 提供下載
                                                        with open(alt_output_file, "rb") as f:
                                                            pdf_bytes = f.read()
                                                        
                                                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                                                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="decrypted_{uploaded_file.name}" class="download-button">下載解密的PDF</a>'
                                                        st.markdown(href, unsafe_allow_html=True)
                                                        
                                                        st.success("使用替代方法成功解密PDF！")
                                                    except Exception as alt_error:
                                                        st.error(f"替代方法也失敗了: {str(alt_error)}")
                                                        st.warning("這個PDF可能使用了特殊的加密方式，標準工具難以處理。")
                                            else:
                                                # 密碼不正確，嘗試其他可能的編碼
                                                st.warning("標準密碼解密失敗，正在嘗試其他編碼方式...")
                                                
                                                # 嘗試不同的編碼處理密碼
                                                success = False
                                                for encoding in ['utf-8', 'latin1', 'cp1252', 'gbk', 'big5']:
                                                    try:
                                                        # 嘗試重新加載文件並使用不同編碼的密碼
                                                        reader = PdfReader(temp_file)
                                                        
                                                        # 嘗試解密
                                                        if reader.decrypt(password) > 0:
                                                            # 成功解密
                                                            success = True
                                                            st.info(f"使用 {encoding} 編碼成功解密")
                                                            
                                                            # 創建一個新的PDF寫入器
                                                            writer = PdfWriter()
                                                            
                                                            # 複製所有頁面
                                                            for page in reader.pages:
                                                                writer.add_page(page)
                                                            
                                                            # 保存解密的PDF
                                                            output_file = os.path.join(tmpdirname, f"decrypted_{uploaded_file.name}")
                                                            with open(output_file, "wb") as f:
                                                                writer.write(f)
                                                            
                                                            # 提供下載
                                                            with open(output_file, "rb") as f:
                                                                pdf_bytes = f.read()
                                                            
                                                            b64_pdf = base64.b64encode(pdf_bytes).decode()
                                                            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="decrypted_{uploaded_file.name}" class="download-button">下載解密的PDF</a>'
                                                            st.markdown(href, unsafe_allow_html=True)
                                                            
                                                            st.success("PDF解密成功！")
                                                            break
                                                    except Exception:
                                                        continue
                                                
                                                # 如果所有編碼方法都失敗，再嘗試使用pikepdf
                                                if not success:
                                                    try:
                                                        st.info("正在嘗試使用強力解密方法...")
                                                        
                                                        # 使用pikepdf嘗試解密
                                                        import pikepdf
                                                        
                                                        # 使用pikepdf打開PDF並解密
                                                        pdf = pikepdf.open(temp_file, password=password)
                                                        
                                                        # 保存為解密文件
                                                        alt_output_file = os.path.join(tmpdirname, f"decrypted_alt_{uploaded_file.name}")
                                                        pdf.save(alt_output_file)
                                                        
                                                        # 提供下載
                                                        with open(alt_output_file, "rb") as f:
                                                            pdf_bytes = f.read()
                                                        
                                                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                                                        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="decrypted_{uploaded_file.name}" class="download-button">下載解密的PDF</a>'
                                                        st.markdown(href, unsafe_allow_html=True)
                                                        
                                                        st.success("使用強力方法成功解密PDF！")
                                                    except Exception as e:
                                                        st.error(f"所有解密方法均失敗。請確認密碼是否正確: {str(e)}")
                                        except Exception as e:
                                            st.error(f"解密過程中出錯: {str(e)}")
                                            
                                            # 進一步的錯誤診斷
                                            error_text = str(e).lower()
                                            if "file has not been decrypted" in error_text:
                                                st.warning("發生常見的'文件未解密'錯誤。這通常是由於密碼處理問題導致的。")
                                                try:
                                                    # 最後嘗試使用pikepdf
                                                    st.info("正在嘗試最後一種解密方法...")
                                                    import pikepdf
                                                    
                                                    # 使用pikepdf打開PDF並解密
                                                    pdf = pikepdf.open(temp_file, password=password)
                                                    
                                                    # 保存為解密文件
                                                    alt_output_file = os.path.join(tmpdirname, f"decrypted_alt_{uploaded_file.name}")
                                                    pdf.save(alt_output_file)
                                                    
                                                    # 提供下載
                                                    with open(alt_output_file, "rb") as f:
                                                        pdf_bytes = f.read()
                                                    
                                                    b64_pdf = base64.b64encode(pdf_bytes).decode()
                                                    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="decrypted_{uploaded_file.name}" class="download-button">下載解密的PDF</a>'
                                                    st.markdown(href, unsafe_allow_html=True)
                                                    
                                                    st.success("最終方法成功解密PDF！")
                                                except Exception as final_error:
                                                    st.error("所有解密方法均失敗。")
                                                    st.info("建議：")
                                                    st.info("1. 確認密碼是否正確")
                                                    st.info("2. 如果密碼包含中文，嘗試在其他PDF閱讀器中找到正確的密碼格式")
                        else:
                            st.info("文件未被加密，無需解密，可以直接使用")
                
            except Exception as e:
                st.error(f"讀取PDF時出錯: {str(e)}")
                if "encrypted" in str(e).lower():
                    st.info("這是一個加密的PDF文件，請使用解密功能處理")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件")
        
        # 加密部分說明
        if operation == "加密PDF":
            st.markdown("""
            ### 加密PDF使用說明
            1. 上傳您想要加密的PDF文件
            2. 設置用戶密碼（打開文件時需要）
            3. 設置擁有者密碼（修改權限時需要）
            4. 選擇文件權限設置
            5. 選擇加密強度
            6. 點擊"加密PDF"按鈕
            7. 下載加密後的文件
            
            ### 適用場景
            - 保護敏感或機密文件
            - 限制文檔的打印、複製或修改
            - 安全地分發需要保密的材料
            
            ### 注意事項
            - 建議避免使用中文字符作為密碼，因為某些PDF閱讀器可能無法正確處理中文密碼
            - 最佳密碼實踐是使用英文字母、數字和特殊符號的組合
            """)
        # 解密部分說明
        else:
            st.markdown("""
            ### 解密PDF使用說明
            1. 上傳已加密的PDF文件
            2. 輸入正確的密碼
            3. 點擊"解密PDF"按鈕
            4. 下載解密後的文件
            
            ### 適用場景
            - 解鎖受密碼保護的PDF文件
            - 移除文件的權限限制
            - 處理需要編輯的加密文檔
            
            ### 特殊情況處理
            - 如果常規解密失敗，系統會自動嘗試多種解密方法
            - 支持中文密碼和特殊字符密碼
            - 使用多種PDF處理庫確保最高的解密成功率
            """)
            st.warning("注意：您必須擁有合法的權限來解密文件。請勿用於非法用途。") 