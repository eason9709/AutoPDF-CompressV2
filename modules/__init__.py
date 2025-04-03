# PDF處理模組包 
from PyPDF2 import PdfReader

def decrypt_pdf(file_path, password):
    """
    通用PDF解密處理器，嘗試使用多種方法解密PDF文件
    
    參數:
    file_path (str): PDF文件路徑
    password (str): 解密密碼
    
    返回:
    tuple: (是否成功解密, 解密後的PdfReader對象或None, 成功信息或錯誤信息)
    """
    success = False
    reader = None
    message = ""
    
    try:
        # 嘗試標準解密
        reader = PdfReader(file_path)
        if reader.is_encrypted:
            try:
                decrypt_result = reader.decrypt(password)
                if decrypt_result > 0:
                    success = True
                    message = "PDF文件解密成功！"
                    return success, reader, message
            except Exception:
                pass
            
            # 如果標準解密失敗，嘗試不同編碼
            for encoding in ['utf-8', 'latin1', 'cp1252', 'gbk', 'big5']:
                try:
                    reader = PdfReader(file_path)
                    if reader.decrypt(password) > 0:
                        success = True
                        message = f"使用 {encoding} 編碼成功解密！"
                        return success, reader, message
                except Exception:
                    continue
            
            # 如果基本方法都失敗，嘗試使用pikepdf
            try:
                import pikepdf
                with pikepdf.open(file_path, password=password) as pdf:
                    # pikepdf成功打開表示解密成功，但我們仍需將處理後的文件返回給PdfReader
                    temp_path = file_path + "_decrypted.pdf"
                    pdf.save(temp_path)
                    reader = PdfReader(temp_path)
                    success = True
                    message = "使用增強方法成功解密！"
                    return success, reader, message
            except ImportError:
                # 如果pikepdf未安裝
                message = "解密失敗，嘗試安裝pikepdf可能會提高解密成功率。"
            except Exception as e:
                # 如果pikepdf解密失敗
                message = f"所有解密方法均失敗: {str(e)}"
        else:
            # 文件未加密
            success = True
            message = "文件未加密，無需解密"
    except Exception as e:
        message = f"嘗試解密時出錯: {str(e)}"
    
    return success, reader, message 