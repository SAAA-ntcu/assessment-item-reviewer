# Language, semantic, and editorial QA

Use this reference for the final language-and-editorial review on every manuscript. Keep this review separate from item correctness, assessment logic, curriculum verification, and teaching alignment so wording problems are not confused with evidence problems.

## 1. Operating principle

Read the manuscript sequentially after substantive review, including sections that received no substantive content comment.

Use five internal classes. Do not display these codes unless requested.

- L1: wrong/missing/repeated words or characters, punctuation, basic proofreading.
- L2: encoding, compatibility characters, symbols, spacing, full-width/half-width, formatting.
- L3: sentence syntax, grammar, modifier attachment, completeness, local semantic clarity.
- L4: referents, comparison objects, role/quantity/category references, materially ambiguous intended meaning.
- L5: paragraph coherence, connectors, repetition, reasoning order, document-level reading flow.

Preserve the author's terminology and professional register. Do not rewrite solely because another sentence sounds smoother.

## 2. L1 surface proofreading

Check for:

- wrong character/word, typo, missing text, duplicated text;
- omitted connective or particle;
- punctuation errors and inconsistent Chinese/English punctuation;
- accidental internal spaces（正文中文字詞句間誤植之無意義半形/全形空格，例如「國小 階段」應改為「國小階段」、「進行 試題 分析」應改為「進行試題分析」；但嚴格排除：(1)段落首行縮排或懸掛縮排空格、(2)表格內部儲存格排版與置中對齊空格、(3)中英文/數字夾雜間之排版微調空格、(4)數學算式與運算符號前後空格、(5)題號或清單序號與標題間隔空格）；
- duplicated punctuation;
- incomplete numbering/list markers;
- residual drafting or production notes.

## 2A. Official formal-report conventions

For author-created formal report prose, apply the official editorial baselines loaded by `SKILL.md`.

- When the official unified-wording source gives a clear low-risk preference, standardize the report accordingly. Example: prefer `部分` over `部份`.
- When the distinction depends on noun/verb status or meaning, determine context before correcting; never blind-replace.
- When the punctuation handbook explicitly permits more than one form, do not call either form wrong. Treat mixed use only as a consistency issue when worth commenting on.
- Preserve verbatim quotations, reproduced source text, formulas, code, URLs, English passages, and discipline-specific notation unless the issue is itself within the review scope or changes meaning.
- Strictly follow the Explicit Exhaustive Annotation Rule: For recurring errors (such as full-width slashes in Western terms, full-width digits, punctuation typos, or wording violations), do NOT consolidate into a single global comment. Flag EVERY SINGLE OCCURRENCE on its exact anchor so the author can review them one by one.

## 3. L2 encoding and formatting QA

Check for:

- Traditional/Simplified Chinese mixing when the report is intended for Taiwan;
- compatibility characters, broken Unicode, OCR/extraction corruption;
- corrupted operators, boxes, fractions, arrows, phonetic/linguistic symbols, science symbols, or other special characters;
- full-width/half-width inconsistency;
- inconsistent number, percentage, unit, item/table/figure/code formatting;
- unstable symbols that may fail across Word/PDF export.

Under the Explicit Exhaustive Annotation Rule, flag every single occurrence of full-width/half-width symbol violations (e.g. Western full-width slashes '／', full-width digits '１２３') across all paragraphs and tables.

## 4. L3 sentence syntax and semantic clarity

Check whether:

- the sentence has a complete grammatical relationship;
- modifiers attach to the intended noun/action/object;
- required words are missing;
- coordinate phrases are parallel;
- logical particles are coherent;
- the sentence can be understood on one normal reading without reconstructing missing structure;
- wording is so awkward that the target-grade subject teacher cannot reliably determine the intended statement.

If the intended meaning cannot be recovered uniquely, require confirmation rather than silently selecting one interpretation.

## 5. L4 referent and intended-meaning QA

Check whether:

- pronouns such as「這些」「其」「上述」have a clear antecedent;
- a person, group, object, category, unit, variable, label, or data series keeps the same role;
- comparison objects are comparable and expressed at the same level;
- an abbreviation/code/symbol is introduced before use;
- two or more materially different readings are plausible.

When multiple meanings are plausible, use a note equivalent to「需回查原意」and offer conditional revisions only when useful.

## 6. L5 paragraph and document coherence

Check whether:

- adjacent sentences form a coherent reasoning sequence;
- connectors such as「因此」「所以」「但是」「另外」「也就是說」match the actual relationship;
- the paragraph keeps a stable focus;
- terminology/referents do not change without explanation;
- a conclusion is supported by preceding evidence;
- repeated sentences/ideas add unnecessary reading load;
- background material interrupts the immediate analytical or instructional line;
- definitions, evidence, interpretation, and teaching action appear in a usable order;
- one paragraph contradicts another.

A coherence issue may be substantive. If it changes item interpretation, data interpretation, teaching alignment, answer validity, or curriculum meaning, move it to the main review register.

## 7. Meaning-sensitive escalation

Do not leave an error at minor-copyedit level merely because it looks typographical.

Escalate when wording changes or can change:

- answer/option validity;
- item roles or labels;
- numbers, percentages, units, categories, conditions, or comparison basis;
- curriculum code/stage claim;
- diagnostic/interpretive conclusion;
- teaching recommendation.

## 8. Professional vs. inappropriate wording

Do not use a blacklist approach.

The following are not inappropriate by themselves when objectively used:

- 困難
- 較困難
- 不易
- 待加強
- 認知負荷較高
- 表現較弱 / 表現較低
- 高分組 / 低分組

Flag wording as inappropriate only when it is genuinely demeaning, insulting, discriminatory, stigmatizing, mocking, moralizing, or an unnecessary personal/character label.

## 9. Correction decision rule

1. Unambiguous mechanical correction: give the direct correction.
2. Meaning clear but wording awkward: propose the smallest useful revision.
3. Two or more materially different meanings plausible: do not choose silently; require confirmation.
4. Wording changes substantive interpretation: classify as substantive, not merely language correction.
5. Wording is already clear and professional: normally do not comment.

## 10. Source-render verification

Do not flag a character as a source-document typo solely because parsed text looks abnormal.

When a rendered DOCX/PDF/page image is available:

1. compare suspicious extracted text with the rendered source;
2. if the rendered source is correct and only extraction is corrupted, do not ask the author to change the manuscript;
3. if the rendered source is also abnormal, report the source issue;
4. if verification is impossible, label it as an encoding/display issue requiring confirmation.

## 11. Output handling

For full-document review:

- keep substantive issues in the main item/section review register;
- enforce the Explicit Exhaustive Annotation Rule (零去重、每一處皆須獨立抓出)：凡是西文斜線「／」混用、全形數字「１２３」、錯別字或標點符號違規，嚴禁以概括性方式整合為單一全域批註，每一處均必須精確錨定並建立獨立批註，便於作者逐一驗收修改；
- elevate language issues when they change item/data/curriculum/teaching interpretation.

For simple corrections, use `位置 / 原文 / 建議` when helpful.
For semantic ambiguity/coherence, use `位置 / 原文 / 問題 / 建議` when helpful.
