# Cross-agent runtime guide

Use this guide in ChatGPT Work, Codex, Gemini CLI, Antigravity-like file workflows, or another Agent Skills-compatible file runtime.

## Portable core

- `SKILL.md` — workflow and rules;
- `references/` — subject routing, curriculum sources, rubric, examples, language QA, runtime guidance;
- `scripts/` — deterministic DOCX comment insertion/extraction/verification helpers.

`agents/openai.yaml` is OpenAI UI metadata only.

## Invariant review behavior

Regardless of runtime:

1. Treat the actual item as primary evidence.
2. Apply the subject route before deciding curriculum-review depth.
3. Separate assessment objective, item analysis, option/distractor reasoning, statistics, and teaching recommendations.
4. Use uncertainty language for inferred response processes.
5. Run item/data/logical consistency QA before style-only rewriting.
6. Run Language & Semantic QA across the full requested scope.
7. Frame substantive comments around the target-grade subject teacher's reading problem.
8. Preserve source text in Stage 1 and add true Word comments only.
9. Preserve existing comments and avoid duplicates.
10. Flag uncertainty rather than inventing unavailable subject evidence.

## Capability gate before full DOCX review

### A. Source access

The runtime must be able to read the source DOCX and relevant references.

### B. Visual/formula/media inspection

Parsed text is not sufficient when an item depends on images, formulas, tables, phonetic notation, charts, diagrams, or other layout-sensitive content.

Use rendered pages/document previews when possible. If visual/media inspection is unavailable, do not guess; mark the affected claim for verification.

### C. Word-comment writing

Prefer a native Word-comment tool only when it reliably creates true OOXML comments and preserves existing comments. Otherwise use the bundled scripts.

Portable workflow:

1. Draft a JSON comment specification with unique anchors.
2. Validate anchor uniqueness when practical.
3. Run `scripts/comments_add.py` with `--spec`, `--require_all`, and `--require_unique`.
4. Extract comments with `scripts/comments_extract.py`.
5. Verify source/output invariants with `scripts/docx_comment_verify.py`.

### D. Output preservation

Never overwrite the source by default. Create a new annotated DOCX.

### E. Failure mode

If true Word comments cannot be written or verified, stop and report the limitation. Do not silently return TXT/Markdown, tracked changes, inline notes, or a visually similar substitute.

## Runtime notes

### ChatGPT Work

Use the installed Skill directly. Prefer the uploaded/current DOCX as source. Return the annotated DOCX as the primary deliverable.

### Codex

Work from explicit input/output paths. Use local/project file access, Python 3, and bundled scripts for deterministic comment handling when needed. Do not edit unrelated repository files.

### Gemini CLI / compatible CLI agents

Treat the Skill as an Agent Skills-compatible directory. The portable core does not depend on OpenAI metadata. Use explicit input/output paths and bundled Python scripts when no reliable native Word-comment writer exists.

Do not assume a chat-only web Gem is equivalent to a file-oriented Agent Skills runtime.

## Script portability

The scripts require Python 3 and `lxml`. Use the runtime's available Python 3 command.

Avoid fragile shell quoting for long Traditional-Chinese comments. Prefer JSON `--spec` input.

## Cross-agent regression expectations

A runtime passes when it:

- reaches materially consistent review conclusions from the same evidence;
- applies the same subject-routing policy;
- preserves uncertainty rules;
- preserves existing comments;
- produces true Word comments;
- keeps source body text unchanged in Stage 1;
- verifies comment anchors before delivery;
- refuses unsupported fallback formats unless approved.
