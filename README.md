# PDF工具箱 (PDF Toolkit)

**PDF工具箱**是一個功能強大的多合一PDF處理應用程序，提供多種PDF處理功能，包括合併、分割、壓縮、優化、文字提取等。應用程序基於Python和Streamlit開發，擁有直觀的Web界面，適合各種PDF文檔處理需求。
**本軟體使用AI協助開發**。

## 快速安裝指南
### 所需組件

- [Python 3.9 ~ 3.13](https://www.python.org/downloads/) (必須)
- 選擇適合自己的平台，並且下載安裝包，點兩下運行，記得勾選"加到PATH"等待安裝完畢。
- [Ghostscript](https://ghostscript.com/releases/gsdnld.html) (推薦，用於高級壓縮)
- 選擇適合自己的平台，並且下載安裝包，點兩下運行來安裝。
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip) (可選但不推薦，較為麻煩，用途等於舊版壓縮)
- 解壓到指定目錄（例如`C:\Program Files\poppler`），並將bin目錄添加到系統PATH環境變數

### 手動安裝步驟

1. 安裝Python：[下載Python](https://www.python.org/downloads/) (安裝時勾選「Add Python to PATH」)
2. 解壓縮後，開啟命令提示符並進入該目錄
3. 透過python運行```run_toolkit.py```(即點兩下那一個python文件，應透過python自動打開)
4. 由於技術限制，第一次啟動後需要再次重啟程式才能運行，敬請見諒。

### macOS/Linux用戶(無法驗證正確性，請小心服用)

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

### 如何使用Python啟動腳本 

1. 打開命令提示符或PowerShell
2. 切換到PDF工具箱目錄：`cd 路徑/到/pdf_toolkit`
3. 運行Python腳本：`python run_toolkit.py`

Python啟動腳本的優勢：
- 不會出現中文亂碼問題
- 跨平台兼容（Windows/Mac/Linux）
- 自動檢測並安裝所有依賴
- 提供彩色終端輸出和更詳細的錯誤信息

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

舊版壓縮功能需要安裝Poppler庫，方法已於上方快速安裝指南說明。

**快速檢查Poppler安裝**
在命令提示符中運行：
```
where pdftoppm
pdftoppm -v
```
如顯示版本信息，則安裝成功。

**macOS用戶**
```
brew install poppler
```
檢查：`pdftoppm -v`

**Linux用戶**
預編譯版本：
```
sudo apt-get install poppler-utils
```

官方最新版本：
```
wget https://poppler.freedesktop.org/poppler-25.04.tar.xz
tar -xf poppler-25.04.tar.xz
cd poppler-25.04
./configure
make
sudo make install
```
檢查：`pdftoppm -v`

### 首次使用Python啟動腳本的注意事項

當您第一次使用`run_toolkit.py`啟動程序時：

1. 腳本會自動檢測並安裝多個必要依賴
2. **重要**：安裝完成後，可能需要關閉並重新運行腳本才能正確載入新安裝的庫
3. 如果遇到「ImportError」或相關錯誤，請：
   ```
   關閉命令窗口 → 重新運行 python run_toolkit.py
   ```
4. 在某些系統上，此重新啟動步驟是必須的，與Python的模塊載入機制有關

這僅適用於首次安裝，後續使用時不會有此問題。

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
- 嘗試使用 `run_toolkit.py` 腳本，它會自動檢查環境並提供故障排除指引

### Streamlit啟動後無法自動打開瀏覽器或再次啟動問題
- **如果瀏覽器沒有自動打開**:
  - 手動訪問 http://localhost:8501 或 http://127.0.0.1:8501
  - 如上述地址不可訪問，請嘗試 http://[您的本機IP]:8501
  - 使用`run_toolkit.py`，它包含增強的連接參數設置
  - 使用`run_debug.py`診斷工具，專門解決連接問題
- **如果關閉後無法再次啟動**:
  - 使用`run_toolkit.py`，它會在啟動前自動終止殘留的streamlit進程
  - 如果使用bat文件，關閉後請等待約30秒再重新啟動
  - 如遇到"地址已在使用中"錯誤，請手動終止python進程
  - 不需要重啟整台電腦，只需終止相關進程即可
- **遇到連接被拒絕問題**:
  - 此問題通常與網絡限制或防火牆設置有關
  - 使用`run_toolkit.py`啟動，它已添加特殊連接參數解決此問題
  - 或運行`run_debug.py`診斷工具，它會嘗試多種連接方式

### 批處理腳本顯示亂碼或"不是內部或外部命令"錯誤
- **編碼問題**: 批處理腳本需要使用UTF-8編碼才能正確顯示中文
  - 確保腳本首行包含 `chcp 65001 > nul` 設置編碼為UTF-8
  - 若出現亂碼，請在記事本中打開批處理文件，選擇「另存為」並設置編碼為「UTF-8」
- **PATH問題**: 如果出現「不是內部或外部命令、可運行的程序或批處理文件」
  - 確認Python和相關工具已添加到系統PATH環境變數
  - 嘗試使用完整路徑執行命令: `%USERPROFILE%\AppData\Local\Programs\Python\Python311\Scripts\streamlit.exe run app.py`
  - 或直接使用python執行: `python -m streamlit run app.py`
- **Python版本問題**: Python 3.13可能與某些庫不完全兼容
  - 如果使用Python 3.13遇到問題，建議安裝Python 3.11或3.12版本

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

## 部署到Streamlit Cloud

如果您希望將應用程序部署到Streamlit Cloud上，請遵循以下步驟：

1. 確保您有一個GitHub帳戶並且已經將項目推送到您的GitHub倉庫
2. 確保您的倉庫中包含以下文件：
   - `requirements.txt`：包含Python依賴項
   - `packages.txt`：包含系統依賴項，如ghostscript和poppler-utils
   - `app.py`：您的Streamlit應用程序主文件

### packages.txt文件
在Streamlit Cloud環境中安裝系統級別依賴項需要在項目根目錄中創建`packages.txt`文件。這個文件應該包含需要通過apt-get安裝的包名稱，每行一個。例如：

```
ghostscript
poppler-utils
```

這樣，Streamlit Cloud會在部署時自動安裝這些系統依賴項。

### 注意事項
- 在Streamlit Cloud中，可能需要在代碼中明確指定Poppler和Ghostscript的路徑
- 部署後，如果發現功能無法正常使用，請檢查日誌以獲取詳細錯誤信息
- 某些高級功能可能受到雲環境限制，請相應調整您的代碼
