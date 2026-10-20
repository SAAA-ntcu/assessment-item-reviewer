# Word comment delivery mode

Use this mode for full-document `.docx` review and whenever the user asks for Word 附註、旁註、註解, or comments directly in the source document.

## Default deliverable

Use the uploaded DOCX as the base document, but preserve it. Create an annotated copy:

`<original_stem>_AI校閱結果.docx`

Default Word comment author: `SAAA成果報告校閱AI agent` (initials: `AI`).

Stage 1 changes only the review layer. Do not alter manuscript body text, tables, images, styles, pagination logic, headers/footers, or numbering unless the user explicitly asks for revisions.

Do not return a TXT or Markdown review register in addition to the DOCX unless requested.

## True Word comments only

Use true Word comments, not:

- inline bracketed notes;
- endnotes or footnotes;
- highlighted text plus appended notes;
- tracked changes;
- a separate text file.

Preserve existing comments. Append new reviewer comments without deleting, resolving, or changing existing ones.

## Comment anchor rules

1. Anchor each comment to the smallest stable source text that makes the issue unambiguous.
2. Prefer the exact phrase or sentence that contains the issue.
3. If the environment/tooling can only anchor at paragraph level, choose the shortest uniquely identifiable paragraph and make the comment text identify the precise phrase.
4. For an image, figure, or missing-option problem, anchor to the nearest item statement, figure caption, or prose sentence that refers to the visual.
5. For a table-wide statistical issue, anchor to the table caption or the paragraph that interprets the table.
6. For a cross-item or whole-chapter issue, anchor to the chapter heading, summary paragraph, or a representative repeated statement. Prefix the comment with `整章一致性：` when useful.
7. Do not attach multiple duplicate comments to repeated wording. Use one chapter-level comment if a single global correction is clearer.
8. Before adding a comment, inspect existing comments when possible. Do not duplicate an issue already captured by an existing comment.

## Comment body style

For substantive issues, keep the reader-centered structure:

`讀者閱讀上的問題 → 問題原因/技術診斷 → 修訂方向`

Do not repeat `題號` and `位置` inside every comment when the anchor already identifies them.

For isolated copyedits, be compact:

`建議改為「……」。`

For ambiguous wording:

`目前句意可能有兩種解讀，需回查原意；若原意為……，可改為……。`

Do not display internal A-D or L1-L5 labels unless requested.

## File behavior across agent runtimes

When the runtime can reliably create true Word comments, create the annotated copy and return that file as the primary deliverable. This applies equally to ChatGPT Work, Codex, Gemini CLI, and other file-oriented runtimes.

Do not overwrite the source by default. If the user explicitly requests true in-place overwrite and the environment supports it, overwrite only after preserving a backup or confirming the operation is reversible.

If the environment cannot create true Word comments, do not silently substitute a text review. State that the Word-comment deliverable could not be completed and ask whether a text fallback is acceptable.

## Bundled fallback scripts

### Portable comment specification

For cross-agent reliability, prefer a UTF-8 JSON specification file instead of many shell-quoted `--add` arguments. Use this shape:

```json
[
  {
    "contains": "unique source paragraph text",
    "comment": "繁體中文 Word 附註內容"
  }
]
```

Use `--require_unique` so repeated anchor text is treated as an error rather than silently attaching to the first occurrence. Use a longer anchor or revise the spec if the anchor is ambiguous. Legacy repeated `--add "anchor=comment"` arguments remain supported for compatibility.


When no native comment writer is available, use:

```bash
python scripts/comments_add.py input.docx --out reviewed.docx --author "SAAA成果報告校閱AI agent" \
  --spec comments-to-add.json \
  --require_all --require_unique
```

Choose anchor text long enough to match a unique paragraph. The fallback script attaches the comment to the matched paragraph.

After writing comments, verify them with:

```bash
python scripts/comments_extract.py reviewed.docx --out comments.json
python scripts/docx_comment_verify.py input.docx reviewed.docx --out verification.json
```

Verify:

- the output DOCX opens as a valid ZIP/OOXML package;
- `word/comments.xml` exists;
- the expected number of comments exists;
- each expected comment has an anchor;
- no source comments were removed;
- unmatched anchor warnings are zero for required comments;
- on Windows, run silent Word COM automation verification (`win32com.client.Dispatch("Word.Application")`) to ensure 100% clean opening with 0 repair popups and 0 corruption dialogs.

## Strict OOXML & File Integrity Rules (防檔案毀損鐵則)

1. **Do NOT Unpack/Repack to Disk**:
   Never extract all DOCX files to a temporary directory and re-archive. This breaks media relationships (orphan images like `image20.png` are dropped, shifting `rId` mappings in `document.xml.rels`) and triggers Microsoft Word "Unreadable Content" errors.
2. **Authoritative Insertion Tool**:
   Always use `scripts/comments_add.py`. It streams and selectively modifies only `word/document.xml`, `word/comments.xml`, `[Content_Types].xml`, and `word/_rels/document.xml.rels`, ensuring byte-level preservation of media, styles, and settings.
3. **Comment Metadata Standards**:
   Every `<w:comment>` element MUST include:
   - `w:author="SAAA成果報告校閱AI agent"`
   - `w:initials="AI"`
   - `w:date="YYYY-MM-DDTHH:MM:SSZ"` (ISO 8601 UTC)

## Failure handling

Do not guess an anchor when the same text occurs in multiple unrelated locations. Use a longer unique anchor, another nearby phrase, or a paragraph-level anchor.

If the correct anchor cannot be located reliably, do not attach the comment to the wrong passage. Mark the issue internally as `anchor unresolved` and report that the comment could not be placed reliably.

Do not deliver a Word file with comments attached to unrelated text merely to achieve a complete comment count.
