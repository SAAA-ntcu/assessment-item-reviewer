# Ready-to-use prompts

## 1. Generic full-report prompt

```text
@assessment-item-reviewer

請完成目前上傳之學力檢測分析報告的第一階段完整審查。

科目：[科目]
年級：[年級]
主要讀者：[該年級該科教師]

請依 Skill 的科目路由與通用審查規則完整檢查整份文件，不要抽樣。

以實際試題為主要依據，檢查評量目標、試題/選項分析、數據解讀、教學建議、全文邏輯、教師可讀性與 Language & Semantic QA。

依科目路由決定課綱核對深度；不要把數學的課綱或專業規則套用到其他科目。

保留所有既有 Word 附註；不刪除、不解決、不覆寫、不重複新增已充分指出的相同問題。
不要修改正文。
只在具有實質修訂價值的對應原文加入真正的 Word Comment。

完成後輸出：原檔名_AI校閱結果.docx
不要另外輸出 TXT/Markdown。
```

## 2. Mathematics full-report prompt

```text
@assessment-item-reviewer

請完整審查目前上傳的數學學力檢測分析報告。

年級：[年級]
主要讀者：[該年級數學教師]

除通用審查外，依 Skill 內建的數學正式課綱與課程手冊進行必要的課綱適切性核對。
以實際試題與所有選項為主要判斷依據。

保留正文、格式、圖片、表格與既有 Word 附註，只新增真正的 Word Comment。
輸出：原檔名_AI校閱結果.docx
```

## 3. Science / English / Chinese general-review prompt

```text
@assessment-item-reviewer

請完整審查目前上傳的[自然科/英語/國語文]學力檢測分析報告。

年級：[年級]
主要讀者：[該年級該科教師]

本次依 Skill 的「一般性審查」模式執行：
- 實際試題與報告是否一致
- 評量目標是否對到試題
- 選項/誘答分析是否合邏輯
- 數據與文字解讀是否一致
- 教學建議是否回應前述分析
- 教師閱讀是否清楚、可用
- 全文前後一致性
- Language & Semantic QA

不要自行套用數學專屬的課綱、迷思或教學規則。
若報告明確引用本科技課綱代碼、學習表現、學習內容或學習階段，請使用 Skill 內建的該科正式課綱進行針對性核對；必要時再參考該科課程手冊摘要釐清意涵。不要因此轉成逐題全面課綱稽核，也不要進行超出來源支持的學科專家判斷。

保留正文與既有 Word 附註，只新增真正的 Word Comment。
```

## 4. Resume-after-interruption prompt

```text
請繼續目前中斷的 assessment-item-reviewer 工作。

先確認最後完成的頁面、題號或章節，以及下一個尚未審查的位置，再從下一個位置繼續。
不要重新審查已完成且已確認的內容。
剩餘內容仍須完整審查，不要抽樣。
完成全部項目後再執行跨題一致性與 Language & Semantic QA 最終檢查。
```
