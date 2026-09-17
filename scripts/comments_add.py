#!/usr/bin/env python3
"""Add one or more true Word comments to DOCX paragraphs matched by substring.

Designed as a runtime-neutral fallback for file-oriented agents. It preserves
existing comments and source package parts, adding only the OOXML plumbing
needed for comments.

Preferred cross-agent usage
---------------------------
Create a UTF-8 JSON file:

[
  {"contains": "unique source text", "comment": "review comment"}
]

Then run:

python scripts/comments_add.py input.docx --out reviewed.docx \
  --spec comments.json --require_all --require_unique

Legacy repeated --add "contains=comment" arguments remain supported.

Matching notes
--------------
- Matching is paragraph-based and comments span the whole matched paragraph.
- Visible text in both <w:t> and tracked-deletion <w:delText> is considered.
- Use --require_unique for deterministic placement. If an anchor occurs in
  multiple paragraphs, choose a longer unique source substring instead of
  silently attaching to the first occurrence.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

NS = {"w": W_NS, "r": R_NS, "pr": PKG_REL_NS}


def w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def _xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")


def _read_xml(zin: zipfile.ZipFile, name: str) -> etree._Element:
    return etree.fromstring(zin.read(name))


def _ensure_content_types(ct_root: etree._Element) -> None:
    xpath = "//*[local-name()='Override' and @PartName='/word/comments.xml']"
    if ct_root.xpath(xpath):
        return
    ns = ct_root.nsmap.get(None)
    tag = f"{{{ns}}}Override" if ns else "Override"
    override = etree.Element(tag)
    override.set("PartName", "/word/comments.xml")
    override.set(
        "ContentType",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
    )
    ct_root.append(override)


def _ensure_document_rels(rels_root: etree._Element) -> None:
    rel_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
    for rel in rels_root.xpath("//pr:Relationship", namespaces=NS):
        if rel.get("Type") == rel_type and rel.get("Target") == "comments.xml":
            return
    ids: list[int] = []
    for rel in rels_root.xpath("//pr:Relationship", namespaces=NS):
        m = re.fullmatch(r"rId(\d+)", rel.get("Id", ""))
        if m:
            ids.append(int(m.group(1)))
    new_id = f"rId{(max(ids) + 1) if ids else 1}"
    rel = etree.SubElement(rels_root, f"{{{PKG_REL_NS}}}Relationship")
    rel.set("Id", new_id)
    rel.set("Type", rel_type)
    rel.set("Target", "comments.xml")


def _ensure_comments_root(existing: bytes | None) -> etree._Element:
    if existing is not None:
        return etree.fromstring(existing)
    return etree.Element(w("comments"), nsmap={"w": W_NS})


def _next_comment_id(comments_root: etree._Element) -> int:
    ids: list[int] = []
    for c in comments_root.xpath("//w:comment", namespaces=NS):
        try:
            ids.append(int(c.get(w("id"))))
        except Exception:
            pass
    return (max(ids) + 1) if ids else 0


def _paragraph_text_for_match(p: etree._Element) -> str:
    parts = p.xpath(".//w:t/text() | .//w:delText/text()", namespaces=NS)
    return "".join(parts)


def _add_comment_to_paragraph(p: etree._Element, comment_id: int) -> None:
    crs = etree.Element(w("commentRangeStart"))
    crs.set(w("id"), str(comment_id))
    p.insert(0, crs)

    cre = etree.Element(w("commentRangeEnd"))
    cre.set(w("id"), str(comment_id))
    p.append(cre)

    r_el = etree.SubElement(p, w("r"))
    cr = etree.SubElement(r_el, w("commentReference"))
    cr.set(w("id"), str(comment_id))


def _append_comment(comments_root: etree._Element, comment_id: int, text: str, author: str) -> None:
    c = etree.SubElement(comments_root, w("comment"))
    c.set(w("id"), str(comment_id))
    c.set(w("author"), author)
    c.set(
        w("date"),
        _dt.datetime.now(_dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    )
    p = etree.SubElement(c, w("p"))
    r_el = etree.SubElement(p, w("r"))
    t = etree.SubElement(r_el, w("t"))
    t.text = text


def _load_spec(path: str) -> list[tuple[str, str]]:
    data: Any = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "comments" in data:
        data = data["comments"]
    if not isinstance(data, list):
        raise SystemExit("--spec must contain a JSON list or an object with a 'comments' list")

    adds: list[tuple[str, str]] = []
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"--spec item {i} must be an object")
        contains = item.get("contains")
        comment = item.get("comment")
        if not isinstance(contains, str) or not contains.strip():
            raise SystemExit(f"--spec item {i} has invalid 'contains'")
        if not isinstance(comment, str) or not comment.strip():
            raise SystemExit(f"--spec item {i} has invalid 'comment'")
        adds.append((contains, comment))
    return adds


def _match_paragraphs(doc_root: etree._Element, contains: str, ignore_case: bool) -> list[etree._Element]:
    needle = contains.lower() if ignore_case else contains
    hits: list[etree._Element] = []
    for p in doc_root.xpath(".//w:p", namespaces=NS):
        hay = _paragraph_text_for_match(p)
        hay_cmp = hay.lower() if ignore_case else hay
        if needle in hay_cmp:
            hits.append(p)
    return hits


def add_comments(
    in_docx: str,
    out_docx: str,
    adds: list[tuple[str, str]],
    author: str,
    ignore_case: bool = False,
    require_all: bool = False,
    require_unique: bool = False,
    dry_run: bool = False,
) -> None:
    with zipfile.ZipFile(in_docx, "r") as zin:
        doc_root = _read_xml(zin, "word/document.xml")
        plan: list[tuple[etree._Element, str, str]] = []
        missing: list[str] = []
        ambiguous: list[tuple[str, int]] = []

        for contains, ctext in adds:
            hits = _match_paragraphs(doc_root, contains, ignore_case)
            if not hits:
                missing.append(contains)
                print(f"[warn] no paragraph matched contains={contains!r}")
                continue
            if len(hits) > 1:
                ambiguous.append((contains, len(hits)))
                print(f"[warn] ambiguous paragraph anchor contains={contains!r} matches={len(hits)}")
                if require_unique:
                    continue
            plan.append((hits[0], contains, ctext))

        if require_all and missing:
            raise SystemExit(f"[comments_add] {len(missing)} patterns were not matched: {missing}")
        if require_unique and ambiguous:
            raise SystemExit(
                "[comments_add] ambiguous anchors under --require_unique: "
                + repr(ambiguous)
            )

        print(
            f"[plan] requested={len(adds)} matched={len(plan)} "
            f"missing={len(missing)} ambiguous={len(ambiguous)}"
        )
        if dry_run:
            print("[OK] dry run only; no DOCX written")
            return

        overrides: dict[str, bytes] = {}
        comments_bytes = zin.read("word/comments.xml") if "word/comments.xml" in zin.namelist() else None
        comments_root = _ensure_comments_root(comments_bytes)

        ct_root = _read_xml(zin, "[Content_Types].xml")
        _ensure_content_types(ct_root)
        overrides["[Content_Types].xml"] = _xml_bytes(ct_root)

        rels_name = "word/_rels/document.xml.rels"
        rels_root = _read_xml(zin, rels_name)
        _ensure_document_rels(rels_root)
        overrides[rels_name] = _xml_bytes(rels_root)

        next_id = _next_comment_id(comments_root)
        for p, _contains, ctext in plan:
            cid = next_id
            next_id += 1
            _add_comment_to_paragraph(p, cid)
            _append_comment(comments_root, cid, ctext, author=author)

        overrides["word/document.xml"] = _xml_bytes(doc_root)
        overrides["word/comments.xml"] = _xml_bytes(comments_root)

        with zipfile.ZipFile(out_docx, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                name = info.filename
                if name in overrides:
                    zout.writestr(name, overrides[name])
                else:
                    zout.writestr(name, zin.read(name))
            if "word/comments.xml" not in zin.namelist():
                zout.writestr("word/comments.xml", overrides["word/comments.xml"])

    print(
        f"[OK] wrote {out_docx} "
        f"(added_comments={len(plan)}, unmatched_patterns={len(missing)}, ambiguous_patterns={len(ambiguous)})"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Add multiple true Word comments by paragraph substring match")
    ap.add_argument("in_docx")
    ap.add_argument("--out", required=True)
    ap.add_argument("--author", default="assessment-item-reviewer")
    ap.add_argument("--spec", help="UTF-8 JSON comment specification file")
    ap.add_argument(
        "--add",
        action="append",
        default=[],
        help="Legacy: add a comment as contains=comment text (repeatable)",
    )
    ap.add_argument("--ignore_case", action="store_true", help="Case-insensitive substring matching")
    ap.add_argument("--require_all", action="store_true", help="Fail if any requested anchor does not match")
    ap.add_argument(
        "--require_unique",
        action="store_true",
        help="Fail if any requested anchor matches more than one paragraph",
    )
    ap.add_argument("--dry_run", action="store_true", help="Validate anchors without writing output DOCX")
    args = ap.parse_args()

    adds: list[tuple[str, str]] = []
    if args.spec:
        adds.extend(_load_spec(args.spec))
    for a in args.add:
        if "=" not in a:
            raise SystemExit("--add must be formatted as contains=comment text")
        k, v = a.split("=", 1)
        if not k.strip() or not v.strip():
            raise SystemExit("--add requires non-empty anchor and comment")
        adds.append((k, v))

    if not adds:
        raise SystemExit("Provide --spec and/or at least one --add")

    add_comments(
        args.in_docx,
        args.out,
        adds,
        author=args.author,
        ignore_case=args.ignore_case,
        require_all=args.require_all,
        require_unique=args.require_unique,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
