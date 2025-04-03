import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
import base64
from io import BytesIO
from datetime import datetime

def pdf_metadata_page():
    st.header("📋 PDF元數據編輯")
    st.write("查看和修改PDF文件的元數據信息")
    
    # 文件上傳
    uploaded_file = st.file_uploader("選擇PDF文件", type="pdf")
    
    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # 保存上傳的文件
            temp_file = os.path.join(tmpdirname, uploaded_file.name)
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 讀取PDF
            try:
                reader = PdfReader(temp_file)
                total_pages = len(reader.pages)
                
                st.write(f"文件名: {uploaded_file.name}")
                st.write(f"總頁數: {total_pages}")
                
                # 獲取當前元數據
                metadata = reader.metadata
                
                if metadata:
                    # 顯示當前元數據
                    st.subheader("當前元數據")
                    metadata_dict = {}
                    
                    # 嘗試提取常見元數據字段
                    fields = [
                        ('/Title', '標題'), 
                        ('/Author', '作者'),
                        ('/Subject', '主題'),
                        ('/Keywords', '關鍵字'),
                        ('/Creator', '創建者'),
                        ('/Producer', '生產者'),
                        ('/CreationDate', '創建日期'),
                        ('/ModDate', '修改日期')
                    ]
                    
                    for key, display_name in fields:
                        value = metadata.get(key)
                        if value:
                            # 處理日期格式
                            if key in ['/CreationDate', '/ModDate']:
                                if isinstance(value, str) and value.startswith('D:'):
                                    # 嘗試解析PDF日期格式
                                    try:
                                        date_str = value[2:16]  # 格式如 D:20200131235959
                                        if len(date_str) >= 14:
                                            year = date_str[0:4]
                                            month = date_str[4:6]
                                            day = date_str[6:8]
                                            hour = date_str[8:10]
                                            minute = date_str[10:12]
                                            second = date_str[12:14]
                                            value = f"{year}-{month}-{day} {hour}:{minute}:{second}"
                                    except:
                                        pass  # 如果解析失敗，保留原始值
                            
                            metadata_dict[display_name] = value
                    
                    # 顯示元數據
                    if metadata_dict:
                        for key, value in metadata_dict.items():
                            st.text(f"{key}: {value}")
                    else:
                        st.info("未找到標準元數據")
                    
                    # 顯示所有元數據（可能包含未識別的字段）
                    with st.expander("查看所有元數據"):
                        for key, value in metadata.items():
                            if key not in [item[0] for item in fields]:
                                st.text(f"{key}: {value}")
                else:
                    st.info("此PDF文件沒有元數據")
                
                # 元數據編輯表單
                st.subheader("編輯元數據")
                with st.form("metadata_form"):
                    # 創建編輯字段
                    title = st.text_input("標題", value=metadata.get('/Title', '') if metadata else '')
                    author = st.text_input("作者", value=metadata.get('/Author', '') if metadata else '')
                    subject = st.text_input("主題", value=metadata.get('/Subject', '') if metadata else '')
                    keywords = st.text_input("關鍵字", value=metadata.get('/Keywords', '') if metadata else '')
                    creator = st.text_input("創建者", value=metadata.get('/Creator', '') if metadata else '')
                    producer = st.text_input("生產者", value=metadata.get('/Producer', '') if metadata else '')
                    
                    # 更新創建日期和修改日期
                    update_creation_date = st.checkbox("更新創建日期為當前時間")
                    update_mod_date = st.checkbox("更新修改日期為當前時間", value=True)
                    
                    # 提交按鈕
                    submit_button = st.form_submit_button("更新元數據")
                
                if submit_button:
                    with st.spinner("正在更新元數據..."):
                        try:
                            # 創建一個新的PDF寫入器
                            writer = PdfWriter()
                            
                            # 複製所有頁面
                            for page in reader.pages:
                                writer.add_page(page)
                            
                            # 創建新的元數據
                            writer.add_metadata({
                                '/Title': title,
                                '/Author': author,
                                '/Subject': subject,
                                '/Keywords': keywords,
                                '/Creator': creator,
                                '/Producer': producer
                            })
                            
                            # 更新日期
                            now = datetime.now()
                            date_format = f"D:{now.strftime('%Y%m%d%H%M%S')}"
                            
                            if update_creation_date:
                                writer.add_metadata({'/CreationDate': date_format})
                                
                            if update_mod_date:
                                writer.add_metadata({'/ModDate': date_format})
                            
                            # 保存更新後的PDF
                            output_file = os.path.join(tmpdirname, f"updated_{uploaded_file.name}")
                            with open(output_file, "wb") as f:
                                writer.write(f)
                            
                            # 提供下載
                            with open(output_file, "rb") as f:
                                pdf_bytes = f.read()
                            
                            b64_pdf = base64.b64encode(pdf_bytes).decode()
                            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="updated_{uploaded_file.name}" class="download-button">下載更新後的PDF</a>'
                            st.markdown(href, unsafe_allow_html=True)
                            
                            st.success("PDF元數據更新成功！")
                        
                        except Exception as e:
                            st.error(f"更新元數據時出錯: {str(e)}")
            
            except Exception as e:
                st.error(f"讀取PDF時出錯: {str(e)}")
    else:
        # 顯示使用說明
        st.info("請先上傳PDF文件進行元數據編輯")
        
        st.markdown("""
        ### 使用說明
        1. 上傳PDF文件
        2. 查看當前的元數據信息
        3. 編輯需要修改的元數據字段
        4. 選擇是否更新創建日期和修改日期
        5. 點擊"更新元數據"按鈕
        6. 下載更新後的文件
        
        ### 元數據字段說明
        - **標題**: 文檔的標題
        - **作者**: 文檔的作者
        - **主題**: 文檔的主題或描述
        - **關鍵字**: 用於搜索引擎和分類的關鍵詞
        - **創建者**: 創建文檔的應用程序
        - **生產者**: 生成PDF的工具
        - **創建日期**: 文檔的創建時間
        - **修改日期**: 文檔的最後修改時間
        
        ### 適用場景
        - 更新文檔的作者和標題信息
        - 為文檔添加關鍵字以便於搜索
        - 更新過期的元數據
        - 準備用於發布的文檔
        """) 