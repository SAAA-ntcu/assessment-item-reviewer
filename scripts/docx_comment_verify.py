#!/usr/bin/env python3
"""Verify that a reviewed DOCX preserves source body content and true comments.

Checks:
- both files are valid DOCX/ZIP packages with word/document.xml;
- source body text equals reviewed body text;
- source paragraph count equals reviewed paragraph count;
- every source comment (id/text/author) is still present unchanged;
- reviewed comments exist in word/comments.xml;
- every reviewed comment has a commentRangeStart and commentRangeEnd anchor;
- package parts unrelated to comment plumbing are byte-identical.

This is a deterministic structural check, not a visual-layout renderer.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}

ALLOWED_CHANGED_PARTS = {
    "[Content_Types].xml",
    "word/document.xml",
    "word/_rels/document.xml.rels",
    "word/comments.xml",
}


def w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def _xml(z: zipfile.ZipFile, name: str) -> etree._Element:
    return etree.fromstring(z.read(name))


def _body_text(z: zipfile.ZipFile) -> str:
    root = _xml(z, "word/document.xml")
    return "".join(root.xpath(".//w:body//w:t/text() | .//w:body//w:delText/text()", namespaces=NS))


def _paragraph_count(z: zipfile.ZipFile) -> int:
    root = _xml(z, "word/document.xml")
    return len(root.xpath(".//w:body//w:p", namespaces=NS))


def _comment_text(c: etree._Element) -> str:
    paras = []
    for p in c.xpath("./w:p", namespaces=NS):
        txt = "".join(p.xpath(".//w:t/text()", namespaces=NS)).strip()
        if txt:
            paras.append(txt)
    return "\n".join(paras).strip()


def _comments(z: zipfile.ZipFile) -> dict[str, dict[str, Any]]:
    if "word/comments.xml" not in z.namelist():
        return {}
    root = _xml(z, "word/comments.xml")
    out: dict[str, dict[str, Any]] = {}
    for c in root.xpath(".//w:comment", namespaces=NS):
        cid = c.get(w("id"))
        if cid is None:
            continue
        out[cid] = {
            "author": c.get(w("author")),
            "text": _comment_text(c),
        }
    return out


def _anchors(z: zipfile.ZipFile) -> dict[str, dict[str, int]]:
    root = _xml(z, "word/document.xml")
    starts: dict[str, int] = {}
    ends: dict[str, int] = {}
    refs: dict[str, int] = {}
    for el in root.xpath(".//w:commentRangeStart", namespaces=NS):
        cid = el.get(w("id"))
        if cid is not None:
            starts[cid] = starts.get(cid, 0) + 1
    for el in root.xpath(".//w:commentRangeEnd", namespaces=NS):
        cid = el.get(w("id"))
        if cid is not None:
            ends[cid] = ends.get(cid, 0) + 1
    for el in root.xpath(".//w:commentReference", namespaces=NS):
        cid = el.get(w("id"))
        if cid is not None:
            refs[cid] = refs.get(cid, 0) + 1
    ids = set(starts) | set(ends) | set(refs)
    return {cid: {"start": starts.get(cid, 0), "end": ends.get(cid, 0), "reference": refs.get(cid, 0)} for cid in ids}


def verify(source: str, reviewed: str) -> dict[str, Any]:
    report: dict[str, Any] = {"source": source, "reviewed": reviewed, "checks": {}, "ok": True}
    with zipfile.ZipFile(source, "r") as zs, zipfile.ZipFile(reviewed, "r") as zr:
        for label, z in (("source", zs), ("reviewed", zr)):
            if "word/document.xml" not in z.namelist():
                raise SystemExit(f"{label} is not a valid DOCX with word/document.xml")

        source_text = _body_text(zs)
        reviewed_text = _body_text(zr)
        body_equal = source_text == reviewed_text
        report["checks"]["body_text_unchanged"] = body_equal

        pc_src = _paragraph_count(zs)
        pc_rev = _paragraph_count(zr)
        report["checks"]["paragraph_count"] = {"source": pc_src, "reviewed": pc_rev, "equal": pc_src == pc_rev}

        src_comments = _comments(zs)
        rev_comments = _comments(zr)
        preserved = []
        changed = []
        missing = []
        for cid, meta in src_comments.items():
            if cid not in rev_comments:
                missing.append(cid)
            elif rev_comments[cid] == meta:
                preserved.append(cid)
            else:
                changed.append(cid)
        report["checks"]["comments"] = {
            "source_count": len(src_comments),
            "reviewed_count": len(rev_comments),
            "preserved_source_ids": preserved,
            "missing_source_ids": missing,
            "changed_source_ids": changed,
        }

        anchors = _anchors(zr)
        unanchored = []
        incomplete = []
        for cid in rev_comments:
            a = anchors.get(cid, {"start": 0, "end": 0, "reference": 0})
            if a["start"] == 0 and a["end"] == 0 and a["reference"] == 0:
                unanchored.append(cid)
            elif a["start"] == 0 or a["end"] == 0 or a["reference"] == 0:
                incomplete.append({"id": cid, **a})
        report["checks"]["anchors"] = {
            "reviewed_comment_ids": sorted(rev_comments.keys()),
            "unanchored_ids": unanchored,
            "incomplete": incomplete,
        }

        common_parts = set(zs.namelist()) & set(zr.namelist())
        unexpected_changed = []
        for name in sorted(common_parts):
            if name in ALLOWED_CHANGED_PARTS:
                continue
            if zs.read(name) != zr.read(name):
                unexpected_changed.append(name)
        report["checks"]["unexpected_changed_parts"] = unexpected_changed

        required_ok = (
            body_equal
            and pc_src == pc_rev
            and not missing
            and not changed
            and len(rev_comments) > 0
            and not unanchored
            and not incomplete
            and not unexpected_changed
        )
        report["ok"] = required_ok
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="Verify DOCX comment output preserves source content")
    ap.add_argument("source_docx")
    ap.add_argument("reviewed_docx")
    ap.add_argument("--out", required=True)
    ap.add_argument("--require_new", type=int, default=0, help="Require at least N new comments beyond source count")
    ap.add_argument("--com", action="store_true", help="Perform real Microsoft Word COM opening verification")
    args = ap.parse_args()

    report = verify(args.source_docx, args.reviewed_docx)
    source_count = report["checks"]["comments"]["source_count"]
    reviewed_count = report["checks"]["comments"]["reviewed_count"]
    new_count = reviewed_count - source_count
    report["checks"]["new_comment_count"] = new_count
    if new_count < args.require_new:
        report["ok"] = False
        report["checks"]["require_new_failure"] = {
            "required": args.require_new,
            "actual": new_count,
        }

    if args.com:
        try:
            import win32com.client
            import os
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0
            doc = word.Documents.Open(os.path.abspath(args.reviewed_docx))
            com_comment_count = doc.Comments.Count
            doc.Close(False)
            word.Quit()
            report["checks"]["word_com_verification"] = {
                "com_open_ok": True,
                "com_comment_count": com_comment_count
            }
        except Exception as e:
            report["ok"] = False
            report["checks"]["word_com_verification"] = {
                "com_open_ok": False,
                "error": str(e)
            }

    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{'OK' if report['ok'] else 'FAIL'}] wrote {args.out} (new_comments={new_count})")
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
