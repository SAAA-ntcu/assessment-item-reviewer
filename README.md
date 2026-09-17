# 成果報告審查總編 Skill (Assessment Item Reviewer)

本資料夾為專門用於臺灣國中小學力檢測、成果報告（國語、數學、自然、英語）之 **「學術總編級審查技能包」** ，相容於各類 Agent 體系（Antigravity、Claude Projects / Desktop、Cursor、Codex 等）。

---

## 結構說明

* `SKILL.md`：核心提示詞與規範（包含強制繁體中文、逐筆標註不去重、學術語氣標準、數學公式視覺驗證規範等）。
* `references/`：官方課綱標準（包含 108 課綱各科 PDF、教育部官方標點符號手冊、常用詞審查標準）。
* `scripts/`：無損操作 Word 批註與檢查的 Python 工具集：
  * `add_comments_lxml.py`：以 XML 方式無損寫入真正 Word 批註對話框（具備 N 次重複字元定位記憶，防止同位重疊 Bug）。
  * `check_duplicate_comments.py`：檢查生成的 DOCX 是否有重疊或錯誤堆疊的批註。
  * `docx_to_img.py` / `visual_check.py`：針對數學公式進行 Word COM $\rightarrow$ PDF $\rightarrow$ PNG 視覺渲染除錯工具。
  * `comments_extract.py` / `docx_comment_verify.py`：原廠批註提取與驗證工具。

---

## 如何給其他 Agent 使用？

### 方式 1：在chatGPT(桌面版)中使用
直接將整個 `assessment-item-reviewer` 路徑貼給AI，叫他幫你安裝。

### 方式 2：在 Cursor / Claude Desktop / 一般 LLM 專案中使用
將此資料夾放入專案根目錄，並在系統提示詞（System Prompt / Rules / Memory）中加入：
> 「請參考 `@assessment-item-reviewer/SKILL.md` 規範執行教育評量報告之文字校對、語氣規範與批註寫入任務。」
