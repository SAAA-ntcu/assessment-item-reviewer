"""
Search for text near formula targets across all pages of a DOCX PDF render.
Converts entire doc to PDF then renders each page to find target text context.
"""
import sys
import os
import win32com.client
import pymupdf
import glob

def docx_to_pdf(docx_path, pdf_path):
    docx_path = os.path.abspath(docx_path)
    pdf_path = os.path.abspath(pdf_path)
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(docx_path)
        doc.SaveAs2(pdf_path, FileFormat=17)
        doc.Close()
    finally:
        word.Quit()

def find_and_render_pages(pdf_path, search_terms, out_dir):
    """Find pages containing search terms and render them."""
    os.makedirs(out_dir, exist_ok=True)
    pdf = pymupdf.open(pdf_path)
    found = {}
    
    for page_num, page in enumerate(pdf, 1):
        text = page.get_text()
        for term in search_terms:
            # Strip spaces for matching since formula text is fragmented
            if any(t in text for t in term.split()):
                if term not in found:
                    found[term] = []
                found[term].append(page_num)
                # Render this page
                mat = pymupdf.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img_path = os.path.join(out_dir, f"page_{page_num:03d}.png")
                if not os.path.exists(img_path):
                    pix.save(img_path)
                    print(f"  Rendered page {page_num}")
    
    pdf.close()
    return found

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Find pages in DOCX containing terms and render to PNG images")
    parser.add_argument("docx", nargs="?", help="Path to input DOCX")
    parser.add_argument("--terms", help="Comma-separated search terms (e.g. '圖A,圖B,63300')")
    parser.add_argument("--out", help="Output directory for rendered PNGs")
    args = parser.parse_args()

    if args.docx:
        terms = [t.strip() for t in args.terms.split(",")] if args.terms else [""]
        out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(args.docx)), "vis_rendered")
        pdf_path = os.path.abspath(args.docx).replace(".docx", "_temp_vis.pdf")
        
        print(f"Converting {args.docx} to PDF...")
        docx_to_pdf(args.docx, pdf_path)
        print(f"Scanning pages for terms {terms}...")
        found = find_and_render_pages(pdf_path, terms, out_dir)
        print(f"Results: {found}")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        print(f"Visual check complete. Images saved in: {out_dir}")
    else:
        # Default M8/M7/M4 test targets
        targets = [
            ('學力檢測分析報告_115_M8_良_V2.docx', 'M8主報告', ['2482', '4x2+4x', '2482-']),
            ('學力檢測分析報告_115_M7_良_v2.docx', 'M7主報告', ['123=36', '122=6', '483=16', '48+x=3']),
            ('學力檢測分析報告_115_M4_良_V2.docx', 'M4主報告', ['63300']),
        ]
        
        for docx, label, terms in targets:
            docx_path = os.path.join(r'C:\Users\adminn\Desktop\V2', docx)
            if not os.path.exists(docx_path):
                continue
            pdf_path = docx_path.replace('.docx', '_vis.pdf')
            out_dir = os.path.join(r'C:\Users\adminn\Desktop\V2', f'vis_{label}')
            
            print(f"\nConverting {label}...")
            docx_to_pdf(docx_path, pdf_path)
            print(f"Finding formula pages...")
            found = find_and_render_pages(pdf_path, terms, out_dir)
            print(f"Found: {found}")
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
