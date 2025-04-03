# AI寫的貢獻指南，不保證實際能否運行

感謝您對PDF工具箱的關注！我們歡迎所有形式的貢獻，包括功能請求、問題報告、代碼貢獻和文檔改進。

## 如何貢獻

### 報告問題

如果您發現了問題或有改進建議：

1. 在提交前，請先搜索現有問題，確保不重複報告
2. 使用問題模板提交詳細的描述
3. 包括重現問題的步驟、預期行為和實際行為
4. 添加截圖或日誌等有幫助的信息

### 提交代碼

如果您想貢獻代碼：

1. Fork本倉庫
2. 創建特性分支 (`git checkout -b feature/your-feature-name`)
3. 提交您的更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature-name`)
5. 創建Pull Request

### 開發指南

#### 環境設置

```bash
# 克隆倉庫
git clone https://github.com/yourusername/pdf-toolkit.git
cd pdf-toolkit

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
pip install -e .  # 安裝為可編輯模式
```

#### 代碼風格

- 遵循PEP 8風格指南
- 使用有意義的變量名和函數名
- 為函數和類添加文檔字符串
- 保持代碼整潔和可讀

#### 測試

- 為新功能添加適當的單元測試
- 確保所有測試在提交前通過

```bash
# 運行測試
pytest
```

### 新功能或模塊

如果您想添加新的功能模塊：

1. 在`modules/`目錄下創建新的Python文件
2. 遵循現有模塊的模式和命名風格
3. 在`app.py`中注冊您的模塊
4. 添加適當的文檔和測試

## 文檔貢獻

我們也歡迎文檔改進：

- 修正拼寫或語法錯誤
- 改進現有文檔的清晰度
- 添加使用示例或常見問題解答
- 翻譯文檔到其他語言

## 行為準則

- 尊重所有貢獻者
- 提供建設性的反饋
- 專注於改進項目而非批評他人
- 共同創造積極的社區環境

## 許可證

通過貢獻您的代碼，您同意將其根據[MIT許可證](LICENSE)提供。

感謝您的貢獻！ 
