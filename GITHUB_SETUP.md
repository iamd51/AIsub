# 🚀 GitHub 推送指南

## 方法 1: 自動推送 (推薦)

1. **雙擊 `setup_github.bat`**
2. **按照提示操作**：
   - 輸入 GitHub 用戶名和郵箱
   - 在 GitHub 建立新倉庫
   - 輸入倉庫 URL
3. **完成！**

## 方法 2: 手動推送

### 1. 安裝 Git
下載並安裝：https://git-scm.com/download/win

### 2. 在 GitHub 建立倉庫
1. 登入 GitHub
2. 點擊右上角 "+" → "New repository"
3. 倉庫名稱：`ai-subtitle-generator`
4. 設為 Public
5. 不要勾選 "Initialize with README"
6. 點擊 "Create repository"

### 3. 推送程式碼
在專案資料夾中開啟命令提示字元，執行：

```bash
# 初始化 Git
git init

# 設定使用者資訊
git config user.name "你的GitHub用戶名"
git config user.email "你的GitHub郵箱"

# 添加所有檔案
git add .

# 提交變更
git commit -m "Initial commit: AI Subtitle Generator Tools"

# 添加遠端倉庫 (替換成你的 URL)
git remote add origin https://github.com/你的用戶名/ai-subtitle-generator.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 🔐 認證設定

如果推送時遇到認證問題：

### 使用 Personal Access Token
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. 勾選 `repo` 權限
4. 複製 token
5. 推送時用 token 作為密碼

### 使用 GitHub CLI (推薦)
```bash
# 安裝 GitHub CLI
winget install GitHub.cli

# 登入
gh auth login

# 推送
git push
```

## 📝 後續維護

### 更新程式碼
```bash
git add .
git commit -m "更新說明"
git push
```

### 建立 Release
1. GitHub 倉庫頁面 → Releases → Create a new release
2. Tag version: `v1.0.0`
3. Release title: `AI Subtitle Generator v1.0.0`
4. 描述功能特色
5. 上傳打包檔案 (可選)

## 🎯 建議的倉庫設定

### README.md 徽章
在 README.md 頂部添加：
```markdown
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)
```

### Topics 標籤
在 GitHub 倉庫設定中添加 topics：
- `whisper`
- `subtitle-generator`
- `ai`
- `japanese`
- `video-processing`
- `speech-recognition`

## ❗ 注意事項

1. **不要上傳**：
   - API Keys (已在 .gitignore 中排除)
   - 模型檔案 (太大)
   - 個人影片/音訊檔案

2. **定期更新**：
   - 修復 bug 後推送更新
   - 添加新功能時更新 README
   - 保持版本號同步

3. **安全考量**：
   - 不要在程式碼中硬編碼 API Key
   - 使用環境變數或設定檔
   - 定期檢查依賴套件安全性