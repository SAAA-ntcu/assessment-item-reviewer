import glob
import os
import zipfile
from lxml import etree

V2 = r'C:\Users\adminn\Desktop\V2'
docx_files = glob.glob(os.path.join(V2, '115 *第一階段審查.docx'))

ns = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
}

print("開始檢查 Word 檔案是否有「同位置重複批註」...\n")

for docx in docx_files:
    print(f"Checking: {os.path.basename(docx)}")
    try:
        with zipfile.ZipFile(docx, 'r') as z:
            doc_xml = z.read('word/document.xml')
            tree = etree.fromstring(doc_xml)
            
            # Find all commentRangeStart elements
            starts = tree.xpath('//w:commentRangeStart', namespaces=ns)
            
            # Group by parent paragraph
            para_comments = {}
            for start in starts:
                c_id = start.get(f'{{{ns["w"]}}}id')
                p = start.getparent()
                while p is not None and p.tag != f'{{{ns["w"]}}}p':
                    p = p.getparent()
                
                if p is not None:
                    # Get the string content of the paragraph up to this comment start
                    # to approximate its physical position
                    preceding_text = "".join(p.xpath('.//w:t/text()', namespaces=ns))
                    if p not in para_comments:
                        para_comments[p] = []
                    para_comments[p].append(c_id)
            
            # Check if any paragraph has multiple comments and if they target the exact same text
            # For simplicity, we check if there are multiple commentRangeStarts adjacent to each other
            
            # Better check: scan the XML elements sequentially
            duplicate_found = False
            for p in tree.xpath('//w:p', namespaces=ns):
                active_comments = set()
                text_since_start = {c: [] for c in active_comments}
                
                # Iterate children of paragraph
                for child in p:
                    if child.tag == f'{{{ns["w"]}}}commentRangeStart':
                        c_id = child.get(f'{{{ns["w"]}}}id')
                        active_comments.add(c_id)
                        text_since_start[c_id] = []
                    elif child.tag == f'{{{ns["w"]}}}commentRangeEnd':
                        c_id = child.get(f'{{{ns["w"]}}}id')
                        if c_id in active_comments:
                            active_comments.remove(c_id)
                    elif child.tag == f'{{{ns["w"]}}}r':
                        t_nodes = child.xpath('.//w:t', namespaces=ns)
                        text = "".join([t.text for t in t_nodes if t.text])
                        for c_id in active_comments:
                            text_since_start[c_id].append(text)
                
                # Analyze text_since_start for overlapping exactly
                # If two comments cover the exact same text in the same paragraph
                str_texts = {c: "".join(t) for c, t in text_since_start.items() if "".join(t).strip()}
                
                # Find duplicates
                seen_texts = {}
                for c_id, text in str_texts.items():
                    if text in seen_texts:
                        duplicate_found = True
                        print(f"  [!] 發現重複！批註 ID {c_id} 與 ID {seen_texts[text]} 標記了同一個位置的文字：'{text}'")
                    else:
                        seen_texts[text] = c_id
                        
            if not duplicate_found:
                print("  [OK] 沒有發現同位置重複批註。")
            print()
    except Exception as e:
        print(f"Error checking {os.path.basename(docx)}: {e}")

print("檢查完成。")
