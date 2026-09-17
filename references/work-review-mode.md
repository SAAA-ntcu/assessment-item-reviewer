# Full-document and file-oriented agent review mode

Use this workflow for an entire chapter, report, multiple items, or any request that asks a file-oriented agent to carry the review through as a complete task.

## Default operating contract

- Preserve the source document by default.
- For DOCX input, produce an annotated DOCX copy with true Word comments before any body-text revision.
- Treat the actual item/image/text/options/tables as mandatory evidence whenever available.
- Apply `subject-routing.md` before deciding curriculum-review depth.
- Review only issues that materially affect correctness, interpretation, assessment logic, teaching linkage, teacher understanding, or document professionalism.
- Do not create comments merely to fill every section.
- Flag uncertainty/missing evidence instead of guessing.
- Run a final multi-pass language, semantic, and editorial review after substantive review.

## Pass 1: Intake and structure map

1. Identify subject, target grade, report title, item numbers, primary teacher reader, and report scope.
2. Map each item to the fields actually present: curriculum code/learning point, knowledge/cognitive dimension, actual item, answer/options, statistics, assessment objective, item analysis, option/distractor analysis, teaching recommendations.
3. Note missing/unreadable item images, options, answer keys, tables, formulas, or statistics before making claims.
4. Note whether the subject route requires detailed curriculum review or general review.

## Pass 2: Item-level review

For each item with enough evidence:

1. Interpret/solve the item independently to the extent supported by the source.
2. Apply the appropriate curriculum depth from `subject-routing.md`.
3. Review assessment objective.
4. Review item/option/distractor analysis.
5. Review statistics and narrative alignment.
6. Review teaching recommendations.
7. Run item/document consistency QA.
8. Record only material issues.

Do not force a fixed number of comments per item.

## Pass 3: Cross-item substantive QA

After item-level review, inspect the whole report for:

- inconsistent pass/accuracy terminology;
- inconsistent discrimination interpretation;
- repeated generic distractor explanations;
- inconsistent curriculum terminology where curriculum review applies;
- different standards for what belongs in assessment objective vs. teaching recommendation;
- repeated background digressions that increase reading load;
- number, unit, label, category, figure, answer, option, or example inconsistencies;
- duplicated or contradictory teaching advice;
- terminology drift across chapters/items.

Report a repeated pattern once at chapter/document level when that is clearer than duplicating it across items.

## Pass 4: Language, semantic, editorial QA

Run `language-editorial-qa.md` across the full report sequentially.

Perform:

1. Surface/encoding QA.
2. Sentence meaning QA.
3. Paragraph/document coherence QA.

Do not use a blacklist for negative educational terms. Do not rewrite acceptable prose merely for stylistic smoothness.

When a rendered document/page is available, verify suspicious symbols or characters against the rendered source before calling them manuscript errors.

## Internal priority scheme

Use internal priorities only for planning/de-duplication unless the user asks to see them.

- A: correctness/source-authority conflict; answer, item, data, curriculum, or factual inconsistency with clear consequence.
- B: assessment/interpretive logic issue; objective mismatch, unsupported option explanation, data conclusion problem, teaching linkage problem.
- C: teacher-readability/coherence issue with material reading cost.
- D: isolated copyedit/format issue that does not change substantive interpretation.

## Word-comment placement

Follow `word-comment-mode.md`.

Keep the review register internal by default. Preserve existing comments and avoid duplicates.

## Interrupted runs

For long reports, persist enough state to resume:

- last completed page/item/section;
- next unreviewed position;
- any unresolved visual verification issue;
- whether the final cross-item and language passes remain pending.

Do not restart completed work unless the user asks for a fresh full rerun.
