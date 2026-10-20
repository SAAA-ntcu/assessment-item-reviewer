# SAAA 成果報告校閱 AI agent Skill (Assessment Item Reviewer)

本資料夾為專門用於臺灣國中小學力檢測、成果報告（國語、數學、自然、英語）之 **「SAAA 成果報告校閱 AI agent 技能包」** ，相容於各類 Agent 體系（Antigravity、Claude Projects / Desktop、Cursor、Codex 等）。

---

## 核心規範與特色

* **審查署名**：統一署名為 `SAAA成果報告校閱AI agent`（代號縮寫 `AI`）。
* **標準產出**：審查產出檔案統一命名為 `<原檔名>_AI校閱結果.docx`。
* **文句間無意義空格規範**：
  * 精確抓出正文中文字詞間誤植之無意義半形/全形空格（如「國小 階段」->「國小階段」）。
  * 嚴格豁免正常排版空格（段落首行縮排、表格排版置中對齊、中英文夾雜間距、數學算式運算符前後空格、題號/條列序號後空格）。
* **視覺與排版審查防呆機制（Visual Verification Protocol）**：
  * 徹底克服 Word 繪圖層（DrawingML、Shape Canvas、SmartArt、文字方塊、圖片）在純文字提取下的盲區。
  * 建立**視覺防呆門檻**：非肉眼親見，嚴禁單憑純文字判定圖示缺失或圖說不存在。
  * 支援 **Word COM $\rightarrow$ PDF $\rightarrow$ PNG** 高解析度快照渲染管線（`docx_to_img.py`），結合多模態視覺模型進行真實版面核驗。
  * 建立**統整表修改驗收機制**：作者註記「-已修改」者，以驗收核對為主，落實修改即標記 PASS，絕不追加批註。
* **Word 文件結構完整性與毀損防呆（Integrity & COM Verification）**：
  * 嚴禁整包解壓重封導致孤立圖檔遺漏與 `document.xml.rels` 的 `rId` 錯位。
  * 統一採用 `comments_add.py` 串流注入標準 `w:date` 與關係鏈。
  * 交付前支援 Microsoft Word COM Automation 實機背景靜默開啟驗證，確保 0 報錯、0 修復提示。

---

## 結構說明

* `SKILL.md`：核心提示詞與規範（包含強制繁體中文、逐筆標註不去重、學術客觀語氣標準、空格規範、圖表與數學公式視覺審查規範、Word 結構無損保護規範等）。
* `references/`：官方課綱與編校指引（包含 108 課綱各科 PDF、教育部官方標點符號手冊、常用詞審查標準、Word 批註交付規範、全文件審查 SOP 等）。
* `scripts/`：無損操作 Word 批註與檢查的 Python 工具集：
  * `comments_add.py`：【官方黃金標準工具】以串流方式安全寫入真正 Word 批註，完整保護關係鏈與多媒體附件。
  * `docx_comment_verify.py`：驗證輸出 DOCX 之結構完整性、批註錨點，並支援 `--com` 實機 Word 背景調用驗證。
  * `docx_to_img.py` / `visual_check.py`：Word COM $\rightarrow$ PDF $\rightarrow$ PNG 頁面快照渲染工具，支援圖文對照與公式多模態視覺覆核。
  * `ollama_proofread.py`：支援本機純離線 Ollama（如 `qwen2.5:7b`）之「段落級流水線」，供一般文書筆電在零外洩環境下執行常規文字校對與批註。
  * `check_duplicate_comments.py`：檢查生成的 DOCX 是否有重疊或錯誤堆疊的批註。
  * `comments_extract.py`：原廠批註提取工具。

---

## 如何給其他 Agent 使用？

### 方式 1：在 Antigravity 中使用
已自動安裝於 `~/.gemini/config/skills/assessment-item-reviewer`，所有專案與工作區均可全域自動載入。

### 方式 2：在 chatGPT(桌面版) / Cursor / Claude Desktop 中使用
將此資料夾放入專案根目錄，並在系統提示詞（System Prompt / Rules / Memory）中加入：
> 「請參考 `@assessment-item-reviewer/SKILL.md` 規範執行教育評量報告之文字校對、語氣規範與批註寫入任務。」
