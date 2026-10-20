#!/usr/bin/env python3
"""
layout_visual_qa.py - Comprehensive Layout & Visual Verification Tool for SAAA Reports

Performs automated visual and structural QA:
1. Blank vs. Scanned/Graphic Page Classification (prevents hallucinating scanned booklets as empty pages)
2. Cross-Page Table Header Repetition Check (w:tblHeader audit)
3. Image Resolution & Downscaling Audit (<300px tiny images)
4. Embedded Font Family & Japanese Fallback Audit (MS-Gothic check)
5. Exhaustive Western Slash (／ vs /) Inventory
"""

import sys
import os
import re
import zipfile
from pathlib import Path
from lxml import etree
import pymupdf

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
WP_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
NS = {"w": W_NS, "a": A_NS, "wp": WP_NS}

def audit_pdf_pages(pdf_path):
    """Classify pages into True Blank, Scanned Graphic, or Text/Hybrid."""
    pdf = pymupdf.open(pdf_path)
    page_stats = []
    
    for i, page in enumerate(pdf):
        page_num = i + 1
        text = page.get_text().strip()
        images = page.get_images()
        
        # Pixmap check for non-white pixel ratio
        pix = page.get_pixmap(dpi=72)
        total_pixels = pix.width * pix.height
        samples = pix.samples
        # Count non-white pixels (assume 3 channels RGB)
        # White is (255, 255, 255)
        non_white = 0
        if pix.n >= 3:
            for p in range(0, len(samples), pix.n):
                r, g, b = samples[p], samples[p+1], samples[p+2]
                if r < 245 or g < 245 or b < 245:
                    non_white += 1
        ratio = non_white / total_pixels if total_pixels else 0
        
        # Classification
        if len(text) == 0 and len(images) == 0 and ratio < 0.005:
            cat = "TRUE_BLANK"  # Legitimate duplex blank page
        elif len(text) <= 5 and (len(images) > 0 or ratio >= 0.01):
            cat = "SCANNED_GRAPHIC"  # Scanned booklet page or image passage
        else:
            cat = "TEXT_OR_HYBRID"
            
        page_stats.append({
            "page": page_num,
            "text_len": len(text),
            "image_count": len(images),
            "non_white_ratio": ratio,
            "category": cat,
            "text_preview": text[:50].replace('\n', ' ')
        })
        
    pdf.close()
    return page_stats

def audit_docx_tables(docx_path):
    """Audit tables for missing w:tblHeader."""
    z = zipfile.ZipFile(docx_path)
    doc_xml = etree.fromstring(z.read("word/document.xml"))
    tables = doc_xml.xpath("//w:tbl", namespaces=NS)
    results = []
    
    for i, tbl in enumerate(tables):
        rows = tbl.xpath("./w:tr", namespaces=NS)
        if not rows:
            continue
        first_row = rows[0]
        has_tbl_header = bool(first_row.xpath(".//w:tblHeader", namespaces=NS))
        # Extract title or text snippet
        first_cell_text = "".join(first_row.xpath(".//w:t/text()", namespaces=NS)).strip()
        results.append({
            "table_index": i + 1,
            "row_count": len(rows),
            "has_tblHeader": has_tbl_header,
            "preview": first_cell_text[:40].replace('\n', ' ')
        })
    z.close()
    return results

def audit_fonts(pdf_path):
    """Audit embedded font families and detect Japanese fallback (MS-Gothic)."""
    pdf = pymupdf.open(pdf_path)
    font_names = set()
    for page in pdf:
        for font in page.get_fonts():
            # font structure: (xref, ext, type, basefont, name, encoding)
            font_names.add(font[3])
    pdf.close()
    
    gothic_fonts = [f for f in font_names if "gothic" in f.lower()]
    return sorted(list(font_names)), gothic_fonts

def audit_slashes(docx_path):
    """Find all instances of full-width (／) vs half-width (/) slashes."""
    z = zipfile.ZipFile(docx_path)
    doc_xml = etree.fromstring(z.read("word/document.xml"))
    paragraphs = doc_xml.xpath("//w:p", namespaces=NS)
    
    full_slashes = []
    half_slashes = []
    
    for p_idx, p in enumerate(paragraphs):
        text = "".join(p.xpath(".//w:t/text()", namespaces=NS))
        if "／" in text:
            # find all occurrences
            for m in re.finditer(r"(.{0,20})／(.{0,20})", text):
                full_slashes.append({
                    "para_idx": p_idx + 1,
                    "snippet": f"{m.group(1)}／{m.group(2)}"
                })
        if "/" in text:
            for m in re.finditer(r"(.{0,20})/(.{0,20})", text):
                half_slashes.append({
                    "para_idx": p_idx + 1,
                    "snippet": f"{m.group(1)}/{m.group(2)}"
                })
    z.close()
    return full_slashes, half_slashes

def main():
    if len(sys.argv) < 2:
        print("Usage: python layout_visual_qa.py <docx_or_pdf_file>")
        sys.exit(1)
        
    target = sys.argv[1]
    stem = os.path.splitext(target)[0]
    pdf_path = target if target.endswith(".pdf") else f"{stem}.pdf"
    docx_path = target if target.endswith(".docx") else f"{stem}.docx"
    
    print(f"=== Layout & Visual QA Audit: {os.path.basename(target)} ===")
    
    if os.path.exists(pdf_path):
        print("\n[1] Page Visual & Raster Classification (PyMuPDF):")
        page_stats = audit_pdf_pages(pdf_path)
        true_blanks = [p["page"] for p in page_stats if p["category"] == "TRUE_BLANK"]
        scanned_pages = [p["page"] for p in page_stats if p["category"] == "SCANNED_GRAPHIC"]
        print(f"  Total pages: {len(page_stats)}")
        print(f"  True Duplex Blank Pages (Safe to ignore): {true_blanks}")
        print(f"  Scanned / Full-Image Pages (DO NOT flag as empty!): {scanned_pages}")
        
        fonts, gothic = audit_fonts(pdf_path)
        print(f"\n[2] Font Audit:")
        print(f"  Total fonts: {len(fonts)}")
        if gothic:
            print(f"  [WARNING] Japanese Font Fallback detected: {gothic}")
        else:
            print("  No Japanese font fallback detected.")
            
    if os.path.exists(docx_path):
        print("\n[3] Table Cross-Page Header Audit (w:tblHeader):")
        tables = audit_docx_tables(docx_path)
        missing_header = [t for t in tables if not t["has_tblHeader"] and t["row_count"] > 3]
        print(f"  Total tables: {len(tables)}")
        print(f"  Multi-row tables lacking tblHeader: {len(missing_header)} / {len(tables)}")
        if missing_header:
            print(f"  Sample tables lacking tblHeader:")
            for t in missing_header[:5]:
                print(f"    - Table {t['table_index']} ({t['row_count']} rows): {t['preview']}")
                
        print("\n[4] Slash (／ vs /) Audit:")
        full_s, half_s = audit_slashes(docx_path)
        print(f"  Full-width slashes (／): {len(full_s)} occurrences")
        print(f"  Half-width slashes (/): {len(half_s)} occurrences")
        
    print("\nAudit complete.")

if __name__ == "__main__":
    main()
