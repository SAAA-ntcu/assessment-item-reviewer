# Changelog

## v2.2 — Official Editorial Standards Edition

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
