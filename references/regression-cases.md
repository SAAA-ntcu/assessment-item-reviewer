# Regression cases for v2.0

Use these as behavioral self-checks. They are not answer keys for new items.

## Core cross-subject cases

### Case 1: subject routing

Input:
- subject = mathematics;
- report contains a learning-content code.

Expected:
- run general review;
- load the matching bundled mathematics curriculum and handbook references;
- perform detailed curriculum consistency checks where relevant.

Input:
- subject = science, English, or Chinese;
- no explicit request for deep curriculum adjudication.

Expected:
- run general review;
- do not load mathematics curriculum/handbook rules;
- do not force exhaustive curriculum-code or grade-boundary review;
- perform targeted curriculum verification only when the manuscript makes a concrete claim and an authoritative source is available.

### Case 2: actual item vs. manuscript

Input:
- the report describes an option, number, label, figure, or answer differently from the actual item.

Expected:
- treat the actual item as primary evidence;
- flag the inconsistency;
- explain why the target teacher cannot reliably verify the analysis until the mismatch is fixed.

### Case 3: assessment objective is only response format

Input pattern:
-「本題評量學生能否選出正確答案。」

Expected:
- identify that the wording describes response format rather than the assessed content/process;
- recommend stating what the item actually requires the student to understand, identify, interpret, compare, calculate, or reason about.

### Case 4: distractor analysis is not supported

Input:
- several wrong options receive the same generic explanation although the option structures differ.

Expected:
- distinguish the option patterns when the item supports different plausible paths;
- use uncertainty language when the student's actual process is not observed;
- do not invent a psychological explanation.

### Case 5: performance claim is logically unsupported

Input:
- a manuscript makes a strong performance/ability conclusion that does not follow from the item/data.

Expected:
- handle it under general assessment logic/evidence strength when it materially affects interpretation;
- do not run a mandatory standalone "single-item mastery/deficit" scan across every item;
- do not misclassify the issue as inappropriate language merely because the wording is negative.

### Case 6: data conclusion mismatch

Input:
- prose says Group A is higher, but the table shows Group B is higher;
- or the stated difference does not match the numbers.

Expected:
- flag the data/prose mismatch as substantive;
- do not invent statistical significance or thresholds.

### Case 7: teaching recommendation disconnected

Input:
- item analysis identifies one concrete issue, but the teaching recommendation provides a broad topic lesson unrelated to that issue.

Expected:
- ask for a direct analysis-to-teaching link;
- allow broad background/extension only after the immediate teaching action is clear.

### Case 8: teacher-reader coherence

Input:
- terminology changes across sections without explanation;
- paragraph connectors do not follow the evidence;
- the teacher must backtrack to infer what a pronoun/category refers to.

Expected:
- surface the reading problem;
- identify the wording/structure causing it;
- recommend the minimum useful clarification or reordering.

### Case 9: ordinary professional negative wording

Input:
-「本題較困難。」
-「學生在此類題目上較不易掌握條件關係。」
-「此概念仍有待加強。」

Expected:
- do not flag these terms as inappropriate solely because they are negative;
- check evidence/support separately when relevant.

### Case 10: genuinely inappropriate wording

Input:
-「這些學生太笨所以不會。」
- unsupported moral labels such as「懶惰」「不用心」.

Expected:
- flag the wording as unprofessional/inappropriate;
- recommend neutral, observable language.

### Case 11: extraction anomaly vs. source-document error

Input:
- parsed text contains abnormal glyphs/symbols but rendered DOCX/PDF may be correct.

Expected:
- inspect rendered source when available;
- do not ask the author to change the source if only extraction is corrupted;
- if verification is impossible, mark it as requiring display/encoding confirmation.

### Case 12: do not over-edit acceptable prose

Input:
- sentence is clear, grammatical, professional, and precise, but an alternative might sound smoother.

Expected:
- do not comment merely for stylistic preference.

## Subject-boundary cases

### Case 13: science curriculum is not mathematics curriculum

Input:
- science report uses science learning-performance/content terminology or codes.

Expected:
- do not interpret them using mathematics code logic;
- use science orientation only for broad recognition;
- perform targeted official-source verification only when the source is available and the report makes a concrete curriculum claim.

### Case 14: English curriculum category/stage code

Input:
- English report cites listening/reading/writing or stage-coded learning performance.

Expected:
- recognize the English curriculum has its own category/stage organization;
- do not import mathematics curriculum-boundary rules;
- keep default review general unless targeted verification is warranted.

### Case 15: Chinese report with a concrete curriculum claim

Input:
- Chinese report cites a learning-performance/content code or stage.

Expected:
- keep the overall review general;
- verify the concrete claim against `curriculum-chinese-2018.pdf`;
- use the handbook orientation only to clarify meaning or progression;
- do not force learning performance and learning content into a one-to-one mapping.

### Case 15A: English recurring learning performance across stages

Input:
- the same or similar English learning performance appears at more than one stage.

Expected:
- do not call recurrence an error;
- recognize that stage difficulty/complexity may increase;
- judge the report primarily from the actual item demand and only make a targeted curriculum comment when the source supports it.

### Case 15B: Science achievement labels attributed to curriculum

Input:
- a report states or implies that「基礎／待加強／精熟」are natural-science curriculum categories.

Expected:
- distinguish report/program classification from formal curriculum wording;
- do not attribute those labels to the science curriculum without another authoritative source;
- keep the rest of the science review general.

### Case 15C: Handbook example treated as mandatory format

Input:
- reviewer notices a handbook example using performance, portfolio, or formative assessment.

Expected:
- do not reject a selected-response item merely because the handbook also recommends varied assessment methods;
- evaluate whether the manuscript accurately describes what this item can support;
- treat handbook examples as interpretive guidance, not exclusive requirements.

## Legacy mathematics cases

These protect established mathematics behavior and apply only when subject = mathematics.

### Case 16: irrelevant information + two-step multiplication

Expected:
- distinguish response format from assessment purpose;
- include information selection if the item intentionally contains irrelevant data;
- distinguish stopping after step 1 from using irrelevant information and from completing two operations with the wrong quantity;
- require teaching advice for both multi-step completion and information selection when both appear in the evidence.

### Case 17: multiplication missing digit with carrying

Expected:
- treat a missing-digit vertical multiplication item as more than routine multiplication when cross-column inference is required;
- distinguish ignoring a carry from recognizing a carry but failing to propagate/check the next place;
- verify figure, example number, decomposition, and arithmetic consistency.

### Case 18: fraction with different whole/unit

Expected:
- track the referenced whole/unit rather than treating identical fraction symbols as identical quantities;
- keep curriculum terminology appropriate to the target grade.

### Case 19: integer number-line movement

Expected:
- distinguish position, distance, direction, start point, and end point;
- verify figure and prose consistency;
- keep nonessential later-grade extension secondary.

### Case 20: hidden-digit price comparison

Expected:
- follow the assessment design and grade-level response process;
- verify strict/non-strict comparison boundaries, package quantities, labels, and arithmetic;
- do not replace the intended reasonable method solely because another method is shorter.

## Full-document and Word-comment cases

### Case 21: full DOCX review should not default to TXT

Expected:
- preserve manuscript body;
- add true Word comments to an annotated DOCX copy;
- do not return TXT/Markdown unless requested.

### Case 22: preserve existing comments

Expected:
- keep existing human comments intact;
- append new comments;
- do not resolve, delete, overwrite, rewrite, or duplicate equivalent comments.

### Case 23: ambiguous comment anchor

Expected:
- use a longer unique anchor or stable nearby phrase;
- do not attach to the first occurrence merely because it is convenient.

### Case 24: image/figure issue

Expected:
- if the image itself cannot receive a comment anchor, anchor to the nearest item statement/caption/reference paragraph;
- state what visual evidence needs verification.

### Case 25: recurring cross-item issue

Expected:
- add one chapter/document-level comment when clearer than repeating the same comment across every item.

### Case 26: comment writer unavailable

Expected:
- do not silently substitute plain text;
- report that the requested true-Word-comment deliverable cannot be completed and ask before using a fallback.

### Case 27: runtime-neutral execution

Expected:
- apply the same core rubric and subject-routing policy across ChatGPT Work, Codex, Gemini CLI, and compatible file agents;
- use runtime-specific tool syntax only as implementation detail;
- treat `agents/openai.yaml` as non-operative outside OpenAI runtimes.

### Case 28: native Word writer unavailable but Python available

Expected:
- use the bundled OOXML scripts;
- prefer JSON specs;
- require unique anchors;
- verify comments and body preservation before delivery.

### Case 29: interrupted long review

Expected:
- record last completed item/page and next unreviewed position;
- resume from the next position;
- do not restart completed sections;
- still run final cross-item and language QA when the remaining review is complete.

## Official editorial-standard cases

### Case 30: fixed unified wording across a formal report

Input:
- formal report prose mixes `部分` and `部份`.

Expected:
- prefer `部分` according to the bundled official wording baseline;
- if the pattern repeats widely, add one representative whole-document consistency comment rather than dozens of duplicates;
- do not alter a verbatim quotation solely to normalize the form.

### Case 31: context-dependent wording pair

Input:
- a word pair in the official table has a noun/verb or meaning-based distinction.

Expected:
- determine grammatical/semantic function before recommending a correction;
- do not use blind global replacement.

### Case 32: officially allowed punctuation alternatives

Input:
- a report uses two forms that the official punctuation handbook explicitly allows as alternatives.

Expected:
- do not declare one form incorrect;
- raise only a useful consistency comment if mixed usage reduces professionalism/readability.

### Case 33: Chinese ellipsis in formal prose

Input:
- Chinese report prose uses an ad hoc sequence of periods instead of the official ellipsis form.

Expected:
- recommend the official ellipsis form shown in the bundled punctuation guide;
- do not apply this rule inside code, URLs, formulas, or an English passage.

### Case 34: source/item quotation integrity

Input:
- reproduced item text or a direct quotation uses a form that differs from the report house style.

Expected:
- preserve source fidelity by default;
- if the item itself is under review and the difference materially affects item clarity/validity, review it as an item issue rather than silently normalizing the quotation.

