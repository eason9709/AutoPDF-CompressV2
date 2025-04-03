# PDF工具箱 (PDF Toolkit)

**PDF工具箱**是一個功能強大的多合一PDF處理應用程序，提供多種PDF處理功能，包括合併、分割、壓縮、優化、文字提取等。應用程序基於Python和Streamlit開發，擁有直觀的Web界面，適合各種PDF文檔處理需求。


## 快速安裝指南
### 所需組件

- [Python 3.8 ~ 3.13](https://www.python.org/downloads/) (必須)
- [Ghostscript](https://ghostscript.com/releases/gsdnld.html) (推薦，用於高級壓縮)
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) (可選，用於舊版壓縮)

### 手動安裝步驟

1. 安裝Python：[下載Python](https://www.python.org/downloads/) (安裝時勾選「Add Python to PATH」)
2. 下載PDF工具箱：[下載最新版本](https://github.com/yourusername/pdf-toolkit/releases/latest)
3. 解壓縮後，開啟命令提示符並進入該目錄
4. 運行以下命令安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
5. 啟動應用：
   ```bash
   streamlit run app.py
   ```

### macOS/Linux用戶

```bash
# 安裝必要組件
python -m pip install streamlit PyPDF2 pikepdf pillow reportlab pdf2image

# 安裝Ghostscript (推薦)
# macOS
brew install ghostscript
# Linux
sudo apt install ghostscript

# 安裝Poppler (可選)
# macOS
brew install poppler
# Linux
sudo apt install poppler-utils

# 啟動應用
streamlit run app.py
```

## 主要功能

- **PDF合併**: 將多個PDF文件合併為一個文檔
- **PDF分割**: 將PDF文件分割為多個獨立文檔
- **PDF旋轉**: 旋轉PDF文件中的頁面
- **PDF壓縮與優化**: 減小PDF文件大小並優化內部結構
  - 標準壓縮: 內置多種壓縮級別
  - 目標大小壓縮: 自動調整參數達到指定大小
  - 高級自定義壓縮: 完全控制所有壓縮選項
- **文字提取**: 從PDF文件中提取文字內容
- **轉換為圖片**: 將PDF頁面轉換為圖片格式
- **加密/解密**: 為PDF添加密碼保護或移除保護
- **編輯元數據**: 查看和編輯PDF文件的元數據
- **添加水印**: 為PDF添加文字或圖像水印
- **舊版壓縮**: 基於圖像轉換的傳統壓縮方法，可精確控制輸出大小

## 加密PDF處理功能

本工具箱特色功能之一是**全面支持處理加密的PDF文件**。無論您使用哪種功能模塊，都能自動檢測加密文件並提供解密選項：

- **自動檢測加密狀態**: 上傳PDF時自動檢測是否加密
- **內置解密功能**: 所有模塊（合併、分割、旋轉等）皆支持直接解密處理
- **支持各種密碼類型**: 包括標準密碼、中文密碼和特殊字符密碼
- **多種解密方法**: 使用多層解密技術，大幅提高解密成功率
- **批量處理**: 在合併功能中可同時解密並處理多個加密PDF

這意味著您可以直接處理需要密碼保護的PDF，無需先解密再上傳，大幅簡化工作流程。

## 舊版壓縮功能

舊版壓縮功能是從早期的獨立壓縮工具演化而來，基於圖像轉換方法，專為特定場景設計：

- **精確控制輸出大小**: 可自動調整參數以達到指定的目標大小
  - 智能算法會尋找最佳DPI值，產生**最貼近但不超過**目標大小的文件
  - 保證輸出文件滿足嚴格的大小限制，同時保持最佳可能的圖像質量
- **適合嚴格限制場景**: 特別適合需符合上傳大小限制的情境
- **高度壓縮**: 對掃描文檔和以圖像為主的PDF有極好的壓縮效果
- **自動模式**: 可設定目標文件大小，系統自動找到最佳平衡點

### Poppler依賴

舊版壓縮功能需要安裝Poppler庫：

**Windows用戶**
1. 下載[Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
2. 解壓到指定目錄（例如`C:\Program Files\poppler`）
3. 將bin目錄（如`C:\Program Files\poppler\bin`）添加到系統PATH環境變數

**macOS用戶**
```
brew install poppler
```

**Linux用戶**
```
sudo apt-get install poppler-utils
```

## 使用指南

### 基本使用

1. 從左側菜單選擇所需功能
2. 上傳PDF文件
3. 如果文件已加密，請在提示時輸入密碼
4. 設置處理選項
5. 點擊相應按鈕處理文件
6. 下載處理後的結果

### 處理加密PDF文件

1. 直接上傳加密的PDF文件
2. 系統會自動檢測並提示輸入密碼
3. 輸入正確密碼後，可以正常使用所有功能
4. 對於包含中文字符的密碼，系統會自動嘗試多種編碼方式
5. 合併功能支持批量處理多個加密PDF，可分別設置不同密碼

### 使用舊版壓縮功能

1. 在左側菜單選擇"舊版壓縮"
2. 上傳PDF文件
3. 設置DPI值（較低的DPI產生較小的文件但可能降低質量）
4. 或啟用自動模式，並設定目標文件大小
5. 點擊"開始壓縮"按鈕
6. 下載壓縮後的文件

### 啟動腳本功能說明（僅Windows）

`run_pdf_toolkit.bat` 啟動腳本提供以下功能：

- **環境檢查**: 自動檢測Python和Ghostscript安裝狀態
- **依賴項安裝**: 安裝所需的Python套件
- **故障排除**: 提供清晰的錯誤信息和安裝指引
- **一鍵啟動**: 環境就緒後自動啟動應用程序

### 壓縮與優化功能說明

PDF工具箱提供三種壓縮模式：

- **標準壓縮**: 選擇預設的壓縮級別（輕度、中度、強力、極限）
- **目標大小壓縮**: 設定目標文件大小，系統自動嘗試接近該大小
- **高級自定義壓縮**: 手動調整圖像分辨率、顏色模式、PDF版本等參數
- **舊版壓縮**: 基於圖像轉換，適合需嚴格控制輸出大小的情境

### 提示和技巧

- 對於圖像密集型PDF，壓縮功能效果最佳
- 目標大小壓縮可能需要更長時間處理
- 合併PDF時可以通過界面重新排序文件
- 加密PDF時建議避免使用中文字符作為密碼，某些PDF閱讀器可能無法正確處理
- 如果您忘記了PDF密碼，可以嘗試常用密碼或聯繫文件原作者
- 舊版壓縮功能會將文本轉為圖像，所以不適合需要保留文本可選性的文件

## 常見問題

### 應用程序無法啟動
- 確保Python 3.8+已正確安裝且已添加到PATH環境變數中
- 確保已安裝所有必要的Python套件
- 嘗試使用 `run_pdf_toolkit.bat` 腳本，它會自動檢查環境並提供故障排除指引

### 壓縮功能效果有限
- 壓縮效果取決於PDF文件的內容和結構
- 安裝Ghostscript可顯著改善壓縮效果
- 嘗試不同的壓縮模式和設置
- 對於特殊需求，嘗試使用舊版壓縮功能

### 解密PDF失敗
- 確認密碼輸入正確，注意區分大小寫
- 如果密碼包含中文字符，系統會自動嘗試多種編碼方式
- 對於特殊加密的PDF，嘗試在"加密/解密"專用功能中處理
- 某些高級加密的PDF可能需要專業解密工具

### "舊版壓縮"功能顯示Poppler錯誤
- 確保已安裝Poppler庫
- 確認Poppler的bin目錄已添加到系統PATH
- 如果您剛安裝Poppler，嘗試重新啟動應用或重新啟動電腦

### 需要Ghostscript嗎？
- Ghostscript不是強制性的，但對於高級PDF壓縮和優化功能非常有用
- 若不安裝Ghostscript，標準壓縮功能仍可使用，但效果可能有限
- 對於專業使用，強烈建議安裝Ghostscript

## 技術細節

PDF工具箱使用多種Python庫處理PDF文件：

- **Streamlit**: 用於Web界面
- **PyPDF2/pikepdf**: 用於基本PDF操作和解密
- **Ghostscript**: 用於高級PDF壓縮和優化
- **pdf2image/pytesseract**: 用於OCR和圖像轉換
- **Poppler**: 用於舊版壓縮功能中的PDF到圖像轉換

## 貢獻指南

歡迎貢獻！如果您想改進PDF工具箱，請：

1. Fork本倉庫
2. 創建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟Pull Request

## 許可證

本項目採用MIT許可證 - 詳見 [LICENSE](LICENSE) 文件

## 聯繫方式

如有問題或建議，請提交Issue或直接聯繫項目維護者。

---

**PDF工具箱** - 您的PDF處理一站式解決方案 
