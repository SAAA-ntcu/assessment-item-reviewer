# Changelog

## v2.7 — Proper Noun Marks (私名號／專名號) & Table of Contents Deep Audit Edition

- **Proper Noun Marks (專名號／私名號) & Underline QA Protocol**:
  - Added full specification for Taiwan proper noun marks (專名號／私名號) following Ministry of Education guidelines.
  - Mandated exclusion of titles and honorifics (e.g. `<u>孫中山</u>先生`, `<u>李</u>校長`, `<u>楊</u>醫生`).
  - Added boundary and punctuation leakage prevention (ensuring underlines never spill over to commas, enumeration commas, or brackets).
  - Added Intra-Item Option Synchronicity checking: flags discrepancies when an option stem or choice omits an underline present in other choices (e.g. Grade 3 Chinese Q16 where option 1 omitted the underline on「繽繽」while options 2, 3, 4 had it).
  - Added document-level macro consistency: detects and alerts when Chapter 1 background marks all 18 counties with proper noun marks, while Chapters 2, 5, and 6 leave them completely unmarked.
- **Table of Contents (TOC) & Front Matter Structure Audit**:
  - Traversal of Word `<w:sdt>` containers to overcome the standard python-docx TOC parsing blind spot.
  - Detection of the fatal self-referencing TOC error (e.g. Word indexing「目錄 3」into the TOC itself).
  - Inconsistent tab stop and dot leader audit (identifying rogue manual ruler drag settings such as `pos="1440"` causing leader dots to jam against text).
  - Expanded character spacing (`w:spacing >= 20`) detection on short chapter headings (e.g. loose, detached「柒、 附 錄」).
  - Chapter depth imbalance detection: flags core analytical chapters spanning > 15 pages (e.g. Chapter 4) with zero sub-entries in TOC while 1-page front chapters list sub-entries.
  - Lists of Tables and Figures (表次／圖次) mandate: verifies front matter completeness when reports contain >= 5 tables or >= 3 figures.
- **Tool Enhancement (`scripts/layout_visual_qa.py`)**:
  - Integrated `audit_docx_toc()` and `audit_proper_noun_marks()` into the unified QA CLI tool.

## v2.6 — Visual Snapshot & Layout Integrity Edition (視覺快照光柵辨識與印務排版檢驗版)

- **Scanned Booklet & Graphic Pages Protocol (光柵掃描與題本防呆檢驗規範)**: Resolved the critical LLM pure-text failure mode where pages with zero selectable text (e.g. Reading Passages on P56/P63/P68/P77 and Appendix Official Test Booklets on P97~P112) were falsely hallucinated as "residual empty page breaks". Enforced the Three-Point Verification Rule (text == 0, images == 0, pixel ratio < 0.005) before declaring any page blank.
- **Cross-Page Table Header Audit (`w:tblHeader`)**: Mandated inspection of multi-page item analysis tables for missing header repetition, ensuring teachers do not lose metadata context when reading split tables across pages.
- **Image Resolution & Downscaling Audit**: Enforced minimum readability threshold (>= 300px) for question stem diagrams to prevent blurry or illegible illustrations (e.g. Eng8 Q25).
- **Japanese Font Fallback Audit (`MS-Gothic`)**: Added automated detection for Japanese font substitution triggered by non-standard circled numbers or bullets, recommending standardization to Taiwan system fonts.
- **Automated Diagnostic Tool (`scripts/layout_visual_qa.py`)**: Added integrated script to automatically classify blank vs. scanned pages, audit `tblHeader` compliance, detect font pollution, and extract all slash occurrences.
- **Synchronization of Exhaustive Flagging**: Updated `language-editorial-qa.md` to eliminate legacy deduplication advice and mandate individual annotations for all slash and symbol errors.

## v2.5 — Exhaustive Symbol & Slashes Rule Edition

- **Exhaustive Slashes & Symbols Flagging (西文斜線與全半形符號每一處皆須抓出)**: Eliminated older deduplication/consolidation guidelines for full/half-width symbols. Mandated that all Western slashes (e.g. `have/has/had to`, `Yes/No`, `O/X`, `one/first`), full-width digits (`１２３`), and punctuation violations must be individually anchored and commented at every single occurrence across all paragraphs and tables.
- **Updated Guidelines**: Synchronized `SKILL.md`, `references/language-editorial-qa.md`, and `references/punctuation-guide.md` with the zero-deduplication exhaustive annotation policy.

## v2.4 — Visual Verification, Word Integrity & Dedicated Reviewer Agent Edition

- **Reviewer Persona & Author**: Unified default comment author to `SAAA成果報告校閱AI agent` (initials: `AI`), replacing generic/academic editor names.
- **Output Filename Pattern**: Standardized default annotated output to `<original_stem>_AI校閱結果.docx`.
- **Comprehensive Visual & Layout Protocol**: Added strict 3-step visual verification pipeline (Visual Gate, Snapshot Rendering via `docx_to_img.py`, and Acceptance Checklist Verification for "-已修改" items) to completely eliminate false-positive ghost comments caused by DrawingML/Shape/Canvas invisibility in pure-text parsing.
- **Whitespace Rules (文句間無意義空格規範)**: Explicitly defined mandatory flags for accidental internal spaces breaking Chinese words/sentences while establishing strict exemptions for paragraph indents, table cell layout, alphanumeric spacing, math formulas, and item numbering.
- **Word Document Integrity & COM Verification**: Enforced safe streaming injection via `comments_add.py` (with standard ISO 8601 UTC `w:date` and relationship preservation) to prevent OOXML corruption; added real Microsoft Word COM automation testing (`--com`) to `docx_comment_verify.py`.
- **Global Skill Deployment**: Synchronized skill package to Antigravity global configuration (`~/.gemini/config/skills/assessment-item-reviewer`).

## v2.3 — Confidential Exam & Local Ollama Edition

- Add the supplied official unified-wording table and revised punctuation handbook as bundled editorial source PDFs.
- Add `editorial-style-guide.md`, `unified-wording-guide.md`, and `punctuation-guide.md` for progressive loading during formal-report Language & Semantic QA.
- Add a fixed formal-report preference for `部分` over `部份` while preserving context-sensitive distinctions for noun/verb and meaning-dependent wording pairs.
- Distinguish clear punctuation errors from officially allowed alternatives; allowed alternatives are consistency choices, not automatic errors.
- Protect source fidelity: do not mechanically normalize verbatim quotations, reproduced item text, formulas, code, URLs, English passages, or discipline-specific notation.
- Add regression cases for unified wording, context-dependent wording, punctuation alternatives, ellipsis, and quotation/item-source integrity.
- Preserve v2.1 cross-subject, curriculum, Word-comment, cross-agent, and DOCX-verification behavior.

## v2.1 — Curriculum Reference Enhanced Edition

- Bundle the full official 2018 Chinese, English, and Science curriculum PDFs for targeted verification of concrete curriculum claims.
- Add `chinese-curriculum-orientation.md` and enrich the English/Science curriculum-orientation files.
- Add concise secondary handbook-orientation references for Chinese, English, and Science, distilled from the user-supplied official curriculum handbooks.
- Clarify source hierarchy: formal curriculum governs; curriculum handbooks clarify scope, progression, teaching/assessment interpretation, and examples but do not override the curriculum.
- Preserve general-review default for Chinese, English, and Science; do not turn bundled sources into an automatic exhaustive curriculum audit.
- Add subject-specific cautions: Chinese learning performance/content need not be one-to-one; English performances may recur across stages with increasing difficulty/complexity; Science curriculum does not itself define report achievement labels such as「基礎／待加強／精熟」.
- Keep v2.0 cross-subject review logic, Word-comment delivery, cross-agent runtime behavior, and mathematics detailed curriculum route unchanged.

## v2.0 — Cross-Subject General Review Edition

- Reframe the Skill from mathematics-only review to a cross-subject assessment-report review framework.
- Make the target reader the teacher of the specified grade and subject.
- Add `subject-routing.md` so curriculum-review depth varies by subject instead of forcing mathematics rules across all subjects.
- Keep detailed mathematics curriculum/handbook verification as the default mathematics route.
- Set science, English, Chinese, and other subjects to general assessment-logic/readability review by default, with targeted curriculum checks only when a concrete curriculum claim/source supports them.
- Add compact science and English curriculum-orientation references based on the supplied official curricula; these are explicitly not complete substitutes for the official PDFs.
- Remove the mandatory standalone single-item mastery/deficit scan; unsupported performance claims are handled under general assessment logic/evidence strength when relevant.
- Generalize the review rubric, error taxonomy, teacher-readability rules, Language & Semantic QA, Work prompts, full-document workflow, and cross-agent runtime guidance.
- Add cross-subject regression cases while retaining legacy mathematics regressions conditionally for mathematics tasks.
- Preserve v1.6 Word-comment scripts, true-DOCX-comment delivery, existing-comment preservation, anchor uniqueness, verification, and resume-after-interruption behavior.

## v1.6 — Cross-Agent Edition

- Make the core workflow explicitly portable across ChatGPT Work, Codex, Gemini CLI, and other Agent Skills-compatible file-oriented runtimes.
- Add a runtime capability gate for source access, visual/formula inspection, true Word-comment writing, output preservation, and failure handling.
- Clarify that `agents/openai.yaml` is OpenAI UI metadata only and is not required by other runtimes.
- Add `references/cross-agent-runtime.md`.
- Add JSON-based portable comment specifications and anchor-uniqueness checking to `comments_add.py`.
- Add deterministic DOCX source/output verification with `docx_comment_verify.py`.
- Make the default Word-comment author runtime-neutral (`assessment-item-reviewer`).

## v1.5 — Word Comment Mode

- Make full-document DOCX review default to true Word comments in an annotated DOCX copy.
- Preserve source body/formatting and existing comments by default.
- Add OOXML comment insertion/extraction fallback scripts and verification rules.

## v1.4 — Language & Semantic QA

- Add multi-pass surface, sentence-semantic, paragraph-coherence, and professional-language QA.
- Add L1-L5 internal language/editing classes and minimum-change/ambiguity rules.
