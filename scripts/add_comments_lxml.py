import zipfile
import sys
import os
import json
import shutil
from lxml import etree
import re

def add_comments_lxml(docx_path, out_path, spec_json_path):
    with open(spec_json_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)
    comments_to_add = spec.get('comments', [])
    if not comments_to_add:
        shutil.copy(docx_path, out_path)
        return
        
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }
    
    temp_zip = out_path + '.temp'
    
    with zipfile.ZipFile(docx_path, 'r') as zin:
        has_comments = 'word/comments.xml' in zin.namelist()
        
        doc_xml = zin.read('word/document.xml')
        doc_tree = etree.fromstring(doc_xml)
        
        if has_comments:
            comments_xml = zin.read('word/comments.xml')
            comments_tree = etree.fromstring(comments_xml)
        else:
            comments_xml = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"></w:comments>'
            comments_tree = etree.fromstring(comments_xml)
            
        rels_xml = zin.read('word/_rels/document.xml.rels')
        rels_tree = etree.fromstring(rels_xml)
        
        content_types = zin.read('[Content_Types].xml').decode('utf-8')
        
    existing_ids = [int(c.get(f"{{{namespaces['w']}}}id")) for c in comments_tree.xpath('.//w:comment', namespaces=namespaces)]
    next_id = max(existing_ids) + 1 if existing_ids else 1
    
    added_count = 0
    seen_texts = {}
    
    for item in comments_to_add:
        search_text = item['contains']
        comment_text = item['comment']
        author = item.get('author', 'SAAA成果報告校閱AI agent')
        initials = item.get('initials', 'AI')
        
        wt_nodes = doc_tree.xpath('.//w:t', namespaces=namespaces)
        full_text = "".join([n.text or "" for n in wt_nodes])
        
        seen_count = seen_texts.get(search_text, 0)
        
        idx = -1
        for _ in range(seen_count + 1):
            idx = full_text.find(search_text, idx + 1)
            if idx == -1:
                break
                
        if idx == -1:
            print(f"Text not found: {search_text} (occurrence {seen_count + 1})")
            continue
            
        seen_texts[search_text] = seen_count + 1
        
        start_idx = idx
        end_idx = idx + len(search_text)
        
        current_len = 0
        start_node = None
        end_node = None
        
        for n in wt_nodes:
            l = len(n.text or "")
            if start_node is None and current_len + l > start_idx:
                start_node = n
            if end_node is None and current_len + l >= end_idx:
                end_node = n
                break
            current_len += l
            
        if start_node is None or end_node is None:
            print(f"Could not resolve nodes for: {search_text}")
            continue
            
        start_r = start_node.getparent()
        range_start = etree.Element(f"{{{namespaces['w']}}}commentRangeStart")
        range_start.set(f"{{{namespaces['w']}}}id", str(next_id))
        start_r.addprevious(range_start)
        
        end_r = end_node.getparent()
        range_end = etree.Element(f"{{{namespaces['w']}}}commentRangeEnd")
        range_end.set(f"{{{namespaces['w']}}}id", str(next_id))
        end_r.addnext(range_end)
        
        ref_r = etree.Element(f"{{{namespaces['w']}}}r")
        ref = etree.Element(f"{{{namespaces['w']}}}commentReference")
        ref.set(f"{{{namespaces['w']}}}id", str(next_id))
        ref_r.append(ref)
        range_end.addnext(ref_r)
        
        new_comment = etree.Element(f"{{{namespaces['w']}}}comment")
        new_comment.set(f"{{{namespaces['w']}}}id", str(next_id))
        new_comment.set(f"{{{namespaces['w']}}}author", author)
        new_comment.set(f"{{{namespaces['w']}}}initials", initials)
        
        p = etree.Element(f"{{{namespaces['w']}}}p")
        r = etree.Element(f"{{{namespaces['w']}}}r")
        t = etree.Element(f"{{{namespaces['w']}}}t")
        t.text = comment_text
        r.append(t)
        p.append(r)
        new_comment.append(p)
        
        comments_tree.append(new_comment)
        next_id += 1
        added_count += 1
        
    if not has_comments and added_count > 0:
        override_str = '<Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>'
        if override_str not in content_types:
            content_types = content_types.replace('</Types>', override_str + '</Types>')
            
        rel_ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
        rel_id = f"rId{len(rels_tree.xpath('.//rel:Relationship', namespaces=rel_ns)) + 1}"
        new_rel = etree.Element(f"{{{rel_ns['rel']}}}Relationship")
        new_rel.set('Id', rel_id)
        new_rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments')
        new_rel.set('Target', 'comments.xml')
        rels_tree.append(new_rel)
        
    with zipfile.ZipFile(docx_path, 'r') as zin, zipfile.ZipFile(temp_zip, 'w') as zout:
        for item in zin.infolist():
            if item.filename not in ['word/document.xml', 'word/comments.xml', 'word/_rels/document.xml.rels', '[Content_Types].xml']:
                zout.writestr(item, zin.read(item.filename))
                
        zout.writestr('word/document.xml', etree.tostring(doc_tree, encoding='utf-8', xml_declaration=True))
        if added_count > 0 or has_comments:
            zout.writestr('word/comments.xml', etree.tostring(comments_tree, encoding='utf-8', xml_declaration=True))
        zout.writestr('word/_rels/document.xml.rels', etree.tostring(rels_tree, encoding='utf-8', xml_declaration=True))
        zout.writestr('[Content_Types].xml', content_types.encode('utf-8'))
        
    os.replace(temp_zip, out_path)

if __name__ == '__main__':
    add_comments_lxml(sys.argv[1], sys.argv[2], sys.argv[3])
