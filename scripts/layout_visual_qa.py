#!/usr/bin/env python3
"""
layout_visual_qa.py - Comprehensive Layout, Visual, TOC & Proper Noun Marks Verification Tool for SAAA Reports

Performs automated visual and structural QA:
1. Blank vs. Scanned/Graphic Page Classification (prevents hallucinating scanned booklets as empty pages)
2. Table of Contents (TOC) & Front Matter Deep Audit:
   - Self-referencing TOC bug detection (e.g., "目錄 3")
   - Dot leader & Tab Stop inconsistency detection
   - Expanded character kerning anomalies (w:spacing on short titles like "柒、附錄")
   - Structural depth & chapter balance (Chapter 4 coverage)
   - Missing Lists of Tables and Figures (表目錄、圖目錄)
3. Cross-Page Table Header Repetition Check (w:tblHeader audit)
4. Image Resolution & Downscaling Audit (<300px tiny images)
5. Embedded Font Family & Japanese Fallback Audit (MS-Gothic check)
6. Exhaustive Western Slash (／ vs /) Inventory
7. Proper Noun Mark (專名號／私名號) & Underline Audit:
   - Run stitching for split words across runs (e.g. 臺 + 中市)
   - Boundary & punctuation leakage check (e.g. <u>臺北市、</u>)
   - Title and honorific inclusion check (e.g. <u>李校長</u> -> <u>李</u>校長)
   - Intra-item option synchronicity check (e.g. Q16 option 1 missing underline on 繽繽 while options 2,3,4 have it)
   - Document-level macro double-standard check (e.g. Chapter 1 underlines 18 counties while later chapters leave all plain)
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
        
        pix = page.get_pixmap(dpi=72)
        total_pixels = pix.width * pix.height
        samples = pix.samples
        non_white = 0
        if pix.n >= 3:
            for p in range(0, len(samples), pix.n):
                r, g, b = samples[p], samples[p+1], samples[p+2]
                if r < 245 or g < 245 or b < 245:
                    non_white += 1
        ratio = non_white / total_pixels if total_pixels else 0
        
        if len(text) == 0 and len(images) == 0 and ratio < 0.005:
            cat = "TRUE_BLANK"
        elif len(text) <= 5 and (len(images) > 0 or ratio >= 0.01):
            cat = "SCANNED_GRAPHIC"
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

def audit_docx_toc(docx_path):
    """Deep audit of Table of Contents (TOC) structure, kerning, tabs, and self-references."""
    results = {
        "has_toc": False,
        "toc_entries": [],
        "self_reference_error": [],
        "spacing_anomalies": [],
        "tab_leader_inconsistencies": [],
        "structural_balance_warnings": [],
        "missing_table_figure_lists": []
    }
    
    z = zipfile.ZipFile(docx_path)
    doc_xml = etree.fromstring(z.read("word/document.xml"))
    
    sdt_tocs = doc_xml.xpath('//w:sdt[.//w:docPartGallery[@w:val="Table of Contents"] or .//w:instrText[contains(., "TOC")]]', namespaces=NS)
    
    toc_paras = []
    if sdt_tocs:
        results["has_toc"] = True
        for sdt in sdt_tocs:
            toc_paras.extend(sdt.xpath('.//w:p', namespaces=NS))
    else:
        t_paras = doc_xml.xpath('//w:p[w:pPr/w:pStyle[contains(translate(@w:val, "TOC", "toc"), "toc")]]', namespaces=NS)
        if t_paras:
            results["has_toc"] = True
            toc_paras.extend(t_paras)
            
    if not results["has_toc"]:
        results["structural_balance_warnings"].append("文檔中未檢測到標準目錄（w:sdt 或 TOC 樣式段落）！")
        z.close()
        return results

    entries = []
    for p_idx, p in enumerate(toc_paras):
        raw_text = "".join(p.xpath('.//w:t/text()', namespaces=NS)).strip()
        if not raw_text:
            continue
            
        pStyle = p.xpath('.//w:pStyle/@w:val', namespaces=NS)
        pStyle_val = pStyle[0] if pStyle else ""
        
        tabs = p.xpath('.//w:tabs/w:tab', namespaces=NS)
        tab_defs = [ (t.attrib.get(f"{{{W_NS}}}val"), t.attrib.get(f"{{{W_NS}}}pos")) for t in tabs ]
        run_tabs = p.xpath('.//w:r/w:tab', namespaces=NS)
        
        spacings = p.xpath('.//w:rPr/w:spacing/@w:val', namespaces=NS)
        bolds = p.xpath('.//w:rPr/w:b', namespaces=NS)
        
        runs_text = [ "".join(r.xpath('.//w:t/text()', namespaces=NS)).strip() for r in p.xpath('.//w:r', namespaces=NS) ]
        runs_text = [ r for r in runs_text if r ]
        
        page_num = None
        title_text = raw_text
        if len(runs_text) >= 2 and runs_text[-1].isdigit():
            page_num = int(runs_text[-1])
            title_text = "".join(runs_text[:-1])
        elif re.search(r'\d+$', raw_text):
            m = re.search(r'^(.*?)(\d+)$', raw_text)
            if m:
                title_text = m.group(1).strip()
                page_num = int(m.group(2))
                
        entry_info = {
            "para_idx": p_idx + 1,
            "raw_text": raw_text,
            "title": title_text,
            "page_num": page_num,
            "style": pStyle_val,
            "tab_defs": tab_defs,
            "run_tabs_count": len(run_tabs),
            "spacing": spacings[0] if spacings else None,
            "bold": bool(bolds)
        }
        entries.append(entry_info)
        
    results["toc_entries"] = entries
    
    # 1. Self-reference check (e.g. 目錄 3)
    for e in entries:
        clean_title = e["title"].replace(" ", "").replace("　", "")
        if clean_title == "目錄" and e["page_num"] is not None:
            results["self_reference_error"].append({
                "para_idx": e["para_idx"],
                "text": e["raw_text"],
                "issue": f"目錄本身被設定為標題階層並列入目錄條目（「{e['raw_text']}」），此為 Word 目錄樣式設定錯誤！"
            })
            
    # 2. Inconsistent custom tab stops across same-style entries
    style_tabs_map = {}
    for e in entries:
        st = e["style"]
        if st not in style_tabs_map:
            style_tabs_map[st] = []
        style_tabs_map[st].append(e)
        
    for st, group in style_tabs_map.items():
        if len(group) >= 2:
            tab_sig_set = set(tuple(e["tab_defs"]) for e in group)
            if len(tab_sig_set) > 1:
                results["tab_leader_inconsistencies"].append({
                    "style": st,
                    "issue": f"同一目錄樣式 [{st}] 內段落之自訂定位點（w:tabs）不一致，導致引導線（Dot Leader）有的緊貼中文字無間隔、有的有空格，視覺上參差脫節。"
                })

    # 3. Spacing anomalies on short headings
    for e in entries:
        if e["spacing"] and int(e["spacing"]) >= 20:
            if len(e["title"]) <= 4:
                results["spacing_anomalies"].append({
                    "para_idx": e["para_idx"],
                    "title": e["title"],
                    "spacing": e["spacing"],
                    "issue": f"短標題「{e['title']}」套用字符間距擴展（w:spacing={e['spacing']}），導致視覺上字面鬆散分散（如「柒 、 附 錄」），易被誤判為手動空格或排版鬆垮。"
                })

    # 4. Structural balance (Chapter 4 coverage)
    ch4_entry = None
    sub_entries_after_ch4 = 0
    in_ch4 = False
    for e in entries:
        t = e["title"]
        if "試題分析" in t or "肆、" in t:
            ch4_entry = e
            in_ch4 = True
            continue
        if in_ch4:
            if any(k in t for k in ["伍、", "陸、", "柒、", "整體學力", "教學建議", "附錄"]):
                in_ch4 = False
            else:
                sub_entries_after_ch4 += 1
                
    if ch4_entry and sub_entries_after_ch4 == 0:
        results["structural_balance_warnings"].append({
            "chapter": ch4_entry["title"],
            "issue": "「試題分析與教學建議」為全書核心章節（篇幅近百頁），但在目錄中完全未展開二級條目（各題號或評量向度），與前三章（篇幅僅1~2頁卻詳列二級子項）形成嚴重結構失衡。"
        })

    # 5. Missing List of Tables / Figures
    tbls = doc_xml.xpath('//w:tbl', namespaces=NS)
    drawings = doc_xml.xpath('//w:drawing | //a:blip', namespaces={"w": W_NS, "a": A_NS})
    
    has_lot = any("表目錄" in e["title"] or "表次" in e["title"] for e in entries)
    has_lof = any("圖目錄" in e["title"] or "圖次" in e["title"] for e in entries)
    
    if len(tbls) >= 5 and not has_lot:
        results["missing_table_figure_lists"].append(f"正文包含 {len(tbls)} 個表格（如表2-1、表3-1、表4-1等），但卷首未編製「表目錄／表次」。")
    if len(drawings) >= 3 and not has_lof:
        results["missing_table_figure_lists"].append(f"正文包含多個統計圖表與試題圖形（如圖5-1學力分布圖），但卷首未編製「圖目錄／圖次」。")

    z.close()
    return results

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

def audit_proper_noun_marks(docx_path):
    """Audit Proper Noun Marks (專名號／私名號) & Underlines for consistency, boundary leaks, and option parity."""
    z = zipfile.ZipFile(docx_path)
    xml = etree.fromstring(z.read("word/document.xml"))
    
    punct_chars = set("，、。！？；：」』）》〉…—～,.!?;:'\")")
    titles = [
        "先生", "女士", "校長", "教授", "醫生", "醫師", "主任", "組長", 
        "院長", "部長", "局長", "課長", "科長", "縣長", "市長", "伯伯", 
        "阿姨", "叔叔", "同學", "老師", "教師", "將軍", "總統", "主席", "隊長"
    ]
    
    counties = [
        "基隆市", "新北市", "臺北市", "台北市", "桃園市", "新竹縣", "新竹市", "苗栗縣", 
        "臺中市", "台中市", "南投縣", "彰化縣", "雲林縣", "嘉義縣", "嘉義市", "臺南市", 
        "台南市", "高雄市", "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "台東縣", "澎湖縣", 
        "金門縣", "連江縣"
    ]
    
    # Filter out TOC sdt paragraphs to avoid polluting chapter detection
    body_paragraphs = xml.xpath('//w:p[not(ancestor::w:sdt)]', namespaces=NS)
    
    underlined_segments = []
    punctuation_leaks = []
    title_inclusions = []
    option_inconsistencies = []
    macro_county_stats = {"ch1_counties": 0, "later_counties_underlined": 0, "later_counties_plain": 0}
    
    item_options = {}
    current_item_key = None
    in_ch1 = False
    
    for p_idx, p in enumerate(body_paragraphs):
        p_text = "".join(p.xpath('.//w:t/text()', namespaces=NS)).strip()
        if not p_text:
            continue
            
        # Detect Chapter transitions cleanly
        if "背景與目的" in p_text:
            in_ch1 = True
        elif in_ch1 and any(h in p_text for h in ["參與縣市與檢測規模", "檢測對象與檢測工具", "試題分析與教學建議", "整體學力表現分析"]):
            in_ch1 = False
            
        runs = p.xpath('.//w:r', namespaces=NS)
        
        # Stitch adjacent runs with underline
        p_underlined_words = []
        curr_text = ""
        curr_u_val = None
        
        for r in runs:
            u = r.xpath('./w:rPr/w:u/@w:val', namespaces=NS)
            t = "".join(r.xpath('.//w:t/text()', namespaces=NS))
            is_u = bool(u and u[0] != "none")
            
            if is_u:
                if curr_u_val == u[0]:
                    curr_text += t
                else:
                    if curr_text:
                        p_underlined_words.append((curr_text, curr_u_val))
                    curr_text = t
                    curr_u_val = u[0]
            else:
                if curr_text:
                    p_underlined_words.append((curr_text, curr_u_val))
                    curr_text = ""
                    curr_u_val = None
        if curr_text:
            p_underlined_words.append((curr_text, curr_u_val))
            
        # Process each stitched underlined word
        for text, u_val in p_underlined_words:
            underlined_segments.append({
                "para_idx": p_idx + 1,
                "text": text,
                "u_val": u_val,
                "context": p_text[:70]
            })
            
            # 1. Punctuation leakage check (leading or trailing punctuation inside underline)
            leaked = [c for c in text if c in punct_chars]
            if leaked:
                punctuation_leaks.append({
                    "para_idx": p_idx + 1,
                    "text": text,
                    "leaked": "".join(leaked),
                    "context": p_text[:70]
                })
                
            # 2. Title inclusion check
            for title in titles:
                if text.endswith(title) and len(text) > len(title):
                    title_inclusions.append({
                        "para_idx": p_idx + 1,
                        "text": text,
                        "title": title,
                        "suggested": f"{text[:-len(title)]}（劃線）+ {title}（不劃線）",
                        "context": p_text[:70]
                    })
                    
            # Track county underlines for macro consistency
            for c in counties:
                if c in text:
                    if in_ch1:
                        macro_county_stats["ch1_counties"] += 1
                    else:
                        macro_county_stats["later_counties_underlined"] += 1

        # Track plain county names in later chapters
        if not in_ch1:
            for c in counties:
                if c in p_text:
                    if not any(c in w[0] for w in p_underlined_words):
                        macro_county_stats["later_counties_plain"] += 1

        # 3. Detect option paragraphs for intra-item option synchronicity
        opt_match = re.match(r'^(?:【?選項\s*([①②③④1234ABCDabcdA-D])】?|[(（]([ABCDabcd1234])[)）]|([①②③④]))[:：、.]?\s*(.*)', p_text)
        if opt_match:
            opt_id = opt_match.group(1) or opt_match.group(2) or opt_match.group(3)
            if opt_id in ['①', '1', 'A', 'a']:
                current_item_key = f"Item_at_P{p_idx+1}"
                item_options[current_item_key] = []
            if current_item_key:
                item_options[current_item_key].append({
                    "para_idx": p_idx + 1,
                    "opt_id": opt_id,
                    "text": p_text,
                    "underlined": [w[0] for w in p_underlined_words]
                })
        else:
            if current_item_key and len(item_options[current_item_key]) >= 2 and not p_text.startswith("選項"):
                current_item_key = None

    # Check option groups for inconsistency
    for item_key, opts in item_options.items():
        if len(opts) < 2:
            continue
        all_underlined = set()
        for opt in opts:
            for u_word in opt["underlined"]:
                if len(u_word) >= 2:
                    all_underlined.add(u_word)
                    
        for target_word in all_underlined:
            opts_with_u = [o["opt_id"] for o in opts if target_word in o["underlined"]]
            opts_with_plain = []
            for o in opts:
                if target_word not in o["underlined"] and target_word in o["text"]:
                    opts_with_plain.append((o["opt_id"], o["para_idx"], o["text"][:60]))
                    
            if opts_with_plain:
                for plain_opt_id, plain_p_idx, snippet in opts_with_plain:
                    option_inconsistencies.append({
                        "item": item_key,
                        "word": target_word,
                        "opts_with_underline": opts_with_u,
                        "missing_opt_id": plain_opt_id,
                        "para_idx": plain_p_idx,
                        "context": snippet,
                        "issue": f"同一試題選項間專名號不一致：選項 {','.join(opts_with_u)} 標有「{target_word}」之專名號（底線），但選項 {plain_opt_id}（P{plain_p_idx}）出現相同專名卻漏劃底線！"
                    })

    # Macro consistency alert
    macro_warnings = []
    if macro_county_stats["ch1_counties"] >= 10 and macro_county_stats["later_counties_plain"] >= 10 and macro_county_stats["later_counties_underlined"] == 0:
        macro_warnings.append({
            "issue": f"全卷專名號雙軌體例矛盾：第壹章前言標註了 {macro_county_stats['ch1_counties']} 處縣市專名號（底線），但後續章節提及相同縣市名 {macro_county_stats['later_counties_plain']} 次均未標註底線。若正式結案報告正文不採用專名號，建議前言統一移除；若採用，則應全卷一致標註。"
        })
        
    z.close()
    return {
        "total_underlined_segments": len(underlined_segments),
        "underlined_segments": underlined_segments,
        "punctuation_leaks": punctuation_leaks,
        "title_inclusions": title_inclusions,
        "option_inconsistencies": option_inconsistencies,
        "macro_warnings": macro_warnings
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python layout_visual_qa.py <docx_or_pdf_file>")
        sys.exit(1)
        
    target = sys.argv[1]
    stem = os.path.splitext(target)[0]
    pdf_path = target if target.endswith(".pdf") else f"{stem}.pdf"
    docx_path = target if target.endswith(".docx") else f"{stem}.docx"
    
    print(f"=== Layout, Visual, TOC & Proper Noun QA Audit: {os.path.basename(target)} ===")
    
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
        print("\n[3] Table of Contents (TOC) & Structure Audit:")
        toc_res = audit_docx_toc(docx_path)
        print(f"  TOC Detected: {toc_res['has_toc']} ({len(toc_res['toc_entries'])} entries)")
        if toc_res["self_reference_error"]:
            print(f"  [FATAL ERROR] Self-referencing TOC bug detected:")
            for s in toc_res["self_reference_error"]:
                print(f"    - P{s['para_idx']}: {s['issue']}")
        if toc_res["tab_leader_inconsistencies"]:
            print(f"  [WARNING] Tab Stop & Dot Leader Inconsistency:")
            for t in toc_res["tab_leader_inconsistencies"]:
                print(f"    - {t['issue']}")
        if toc_res["spacing_anomalies"]:
            print(f"  [NOTICE] Character Kerning / Spacing Anomalies:")
            for sp in toc_res["spacing_anomalies"]:
                print(f"    - P{sp['para_idx']} ({sp['title']}): {sp['issue']}")
        if toc_res["structural_balance_warnings"]:
            print(f"  [WARNING] Structural Balance Warnings:")
            for sb in toc_res["structural_balance_warnings"]:
                print(f"    - {sb if isinstance(sb, str) else sb['issue']}")
        if toc_res["missing_table_figure_lists"]:
            print(f"  [ADVICE] Missing Front Matter Lists:")
            for m in toc_res["missing_table_figure_lists"]:
                print(f"    - {m}")

        print("\n[4] Table Cross-Page Header Audit (w:tblHeader):")
        tables = audit_docx_tables(docx_path)
        missing_header = [t for t in tables if not t["has_tblHeader"] and t["row_count"] > 3]
        print(f"  Total tables: {len(tables)}")
        print(f"  Multi-row tables lacking tblHeader: {len(missing_header)} / {len(tables)}")
        if missing_header:
            print(f"  Sample tables lacking tblHeader:")
            for t in missing_header[:5]:
                print(f"    - Table {t['table_index']} ({t['row_count']} rows): {t['preview']}")
                
        print("\n[5] Slash (／ vs /) Audit:")
        full_s, half_s = audit_slashes(docx_path)
        print(f"  Full-width slashes (／): {len(full_s)} occurrences")
        print(f"  Half-width slashes (/): {len(half_s)} occurrences")
        
        print("\n[6] Proper Noun Mark (專名號／私名號) & Underline Audit:")
        pnm_res = audit_proper_noun_marks(docx_path)
        print(f"  Total underlined segments: {pnm_res['total_underlined_segments']}")
        if pnm_res["punctuation_leaks"]:
            print(f"  [WARNING] Punctuation leakage in proper noun marks ({len(pnm_res['punctuation_leaks'])} found):")
            for pl in pnm_res["punctuation_leaks"][:5]:
                print(f"    - P{pl['para_idx']}: 「{pl['text']}」（包含符號「{pl['leaked']}」）")
        else:
            print("  No punctuation leakage detected.")
            
        if pnm_res["title_inclusions"]:
            print(f"  [WARNING] Titles/Honorifics mistakenly underlined ({len(pnm_res['title_inclusions'])} found):")
            for ti in pnm_res["title_inclusions"][:5]:
                print(f"    - P{ti['para_idx']}: 「{ti['text']}」-> 建議調整為：{ti['suggested']}")
        else:
            print("  No title/honorific inclusion detected.")
            
        if pnm_res["option_inconsistencies"]:
            print(f"  [CRITICAL] Intra-item option proper noun mark inconsistencies ({len(pnm_res['option_inconsistencies'])} found):")
            for oi in pnm_res["option_inconsistencies"]:
                print(f"    - {oi['issue']}")
        else:
            print("  No intra-item option inconsistencies detected.")
            
        if pnm_res["macro_warnings"]:
            print(f"  [POLICY WARNING] Document-level macro double-standard warnings:")
            for mw in pnm_res["macro_warnings"]:
                print(f"    - {mw['issue']}")
        else:
            print("  Macro proper noun mark policy appears consistent.")
            
    print("\nAudit complete.")

if __name__ == "__main__":
    main()
