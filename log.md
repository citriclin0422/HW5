# 2026-06-08 工作紀錄

## 今日成果摘要

今天完成了「十大機器學習演算法互動平台」從專案整理、GitHub 建立、功能擴充，到 Streamlit 部署版本的完整開發流程。

GitHub Repository：

- https://github.com/citriclin0422/HW5

## 1. 建立與整理 GitHub 專案

- 發現目前工作資料夾原先位於另一個 Git repository 內，且原本的 `origin` 指向其他專案。
- 將 `C:\AI_class\HW5_MLtop10` 初始化成獨立 Git repository。
- 將遠端設定為 `https://github.com/citriclin0422/HW5.git`。
- 新增 `.gitignore`，排除：
  - `node_modules`
  - `.next`
  - Python 快取
  - 本機環境變數與 API Key
  - Streamlit Secrets
  - 本機日誌與暫存資料夾
- 將完整專案、研讀報告與資訊圖表推送至 GitHub。

## 2. README 文件更新

- 將原本顯示異常的 README 重寫。
- 最終將 README 完整改寫為繁體中文。
- README 目前包含：
  - 專案介紹
  - 功能特色
  - 技術架構
  - Docker 啟動方式
  - 前後端本機開發方式
  - OpenAI API Key 設定方式
  - Streamlit 本機執行與 Community Cloud 部署步驟
  - API 端點說明
  - 專案結構
  - 研讀資料連結
  - 安全注意事項

## 3. 網站執行與環境問題處理

- 確認 Docker 與 Docker Compose CLI 已安裝。
- 執行 Docker Compose 時，Docker Desktop Linux Engine 回傳 `500 Internal Server Error`。
- 改以本機開發模式啟動：
  - FastAPI：http://localhost:8000
  - Next.js：http://localhost:3000
- 發現原本 Next.js dev server 卡住並出現 `EPIPE`，重新啟動前端程序後恢復正常。
- 驗證：
  - 前端回傳 HTTP `200`
  - API health check 回傳 `{"status":"ok"}`

## 4. AI 學習助理

- 新增 FastAPI AI 問答端點：
  - `POST /api/assistant/ask`
- 新增後端檔案：
  - `backend/app/assistant.py`
- 使用 OpenAI Responses API。
- API Key 僅從後端的 `OPENAI_API_KEY` 環境變數讀取，避免暴露於前端。
- 支援將目前選擇的演算法課程內容加入提問上下文。
- 新增輸入長度驗證、缺少 API Key 提示與上游服務錯誤處理。
- 前端新增 AI 聊天介面：
  - 問題輸入區
  - 建議問題按鈕
  - 對話紀錄
  - 載入狀態
  - 錯誤提示
- 新增 `.env.example` 與 Docker Compose AI 環境變數設定。

## 5. 網頁標題與繁體中文介面

- 將網站標題從「Top10 機器學習互動學習」改為：
  - **十大機器學習演算法互動平台**
- 同步更新瀏覽器 metadata title 與 description。
- 修正主要前端介面的亂碼文案，改為清楚的繁體中文。
- 改善搜尋、篩選、測驗、完成進度與 AI 助理的中文顯示。

## 6. 互動演算法圖表與參數控制

- 在課程內容中加入互動模擬區塊。
- 左側新增參數調整條：
  - 模型複雜度：`10% - 100%`
  - 正則化強度：`0% - 100%`
  - 訓練資料比例：`40% - 90%`
- 右側新增純 React、CSS 與 SVG 製作的互動圖表：
  - 合成資料點分布
  - 模型決策邊界
  - 擬合度
  - 泛化能力
  - 穩定度
- 圖表會隨參數即時更新，不需額外圖表套件。

## 7. Streamlit 部署版本

- 新增可獨立部署的 Streamlit App：
  - `streamlit_app.py`
- Streamlit 版本包含：
  - 十大演算法搜尋與分類
  - 課程選擇
  - 參數調整
  - 即時 SVG 圖表
  - AI 學習助理
- 新增 Streamlit 部署檔案：
  - `requirements.txt`
  - `.streamlit/config.toml`
  - `.streamlit/secrets.toml.example`
- 使用 Streamlit Secrets 管理 `OPENAI_API_KEY`。
- Streamlit 本機網址：
  - http://localhost:8501
- Streamlit health check 回傳 `ok`。

## 8. Oh My OpenCode 安裝嘗試

- 依照使用者要求檢查 `opensoft/oh-my-opencode.git`。
- 確認該專案是 OpenCode plugin，而不是 Codex skill。
- 確認本機 OpenCode `1.15.13`、Node.js 與 npm 已安裝。
- 安裝 Bun `1.3.14`。
- Oh My OpenCode 安裝器仍因子程序找不到 Bun 而失敗。
- 安裝流程被使用者中止，因此 Oh My OpenCode 尚未完成安裝。
- 暫存 clone 資料夾已由 `.gitignore` 排除，不會推送至 GitHub。

## 9. 驗證結果

今日執行並通過：

- `npm run build`
  - Next.js production build 成功
  - TypeScript 檢查成功
- `python -m compileall backend\app`
  - FastAPI 後端編譯成功
- `python -m py_compile streamlit_app.py`
  - Streamlit App 語法檢查成功
- Streamlit `AppTest`
  - `0` 個例外
- `docker compose config`
  - Docker Compose 設定有效
- `git diff --check`
  - 無格式錯誤
- 前端 HTTP 回應：
  - `http://localhost:3000` 回傳 `200`
- FastAPI health check：
  - `http://localhost:8000/api/health` 回傳正常
- Streamlit health check：
  - `http://localhost:8501/_stcore/health` 回傳 `ok`

## 10. 今日 Git 提交

### `c1ebab6 Initial HW5 learning app`

- 建立獨立 HW5 Git repository。
- 加入原始 Next.js、FastAPI、Docker、研讀報告與資訊圖表。
- 首次推送至 GitHub。

### `83d48b6 Add AI assistant and Streamlit deployment`

- 新增 AI 學習助理。
- 新增互動參數與演算法圖表。
- 更新網站標題與主要繁體中文介面。
- 新增 Streamlit 部署版本。
- 將 README 完整改寫為繁體中文。

## 最終狀態

- 完整網站版本可透過 Next.js 與 FastAPI 執行。
- Streamlit 版本可直接部署至 Streamlit Community Cloud。
- 專案已同步至 GitHub。
- API Key、Secrets、快取、依賴與本機日誌均未提交至 GitHub。
