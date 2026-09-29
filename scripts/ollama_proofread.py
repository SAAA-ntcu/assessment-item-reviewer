#!/usr/bin/env python3
"""
純離線 Ollama 常規文字校對與 Word 批註寫入管線 (Offline Ollama Proofreading Pipeline)

特點：
1. 專為「未公開題本」與「敏感機密報告」設計，100% 離線在本地端運行，不聯外網。
2. 採用「段落切分流水線（Paragraph Pipeline）」，每次僅送 100~300 字，
   即使用 7B/14B 等輕量模型（如 qwen2.5:7b）在一般筆電也能超高速、零記憶體溢位運行。
3. 自動比對文字差異並生成座標，使用 add_comments_lxml.py 寫入標準 Word 批註。

使用方式：
python scripts/ollama_proofread.py input.docx --model qwen2.5:7b --url http://localhost:11434
"""

import os
import sys
import json
import zipfile
import argparse
import subprocess
from lxml import etree
import urllib.request
import urllib.error

def call_ollama(prompt, model="qwen2.5:7b", base_url="http://localhost:11434"):
    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            res_obj = json.loads(resp.read().decode("utf-8"))
            return res_obj.get("response", "")
    except urllib.error.URLError as e:
        print(f"[錯誤] 無法連線至本地 Ollama 服務 ({base_url})，請確認 Ollama 是否已啟動。詳細：{e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Ollama 離線 Word 批註校對工具")
    parser.add_argument("input_docx", help="待校對的 Word 檔案路徑")
    parser.add_argument("--out", help="輸出 Word 檔案路徑（預設為 <原檔名>_第一階段審查.docx）")
    parser.add_argument("--model", default="qwen2.5:7b", help="Ollama 模型名稱（預設：qwen2.5:7b）")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama 服務網址")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input_docx)
    if not os.path.exists(input_path):
        print(f"[錯誤] 找不到檔案：{input_path}")
        sys.exit(1)

    out_path = args.out or input_path.replace(".docx", "_第一階段審查.docx")

    # 1. 抽取段落文字
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paragraphs = []
    with zipfile.ZipFile(input_path, 'r') as zin:
        doc_tree = etree.fromstring(zin.read('word/document.xml'))
        for p in doc_tree.xpath('.//w:p', namespaces=ns):
            t_nodes = p.xpath('.//w:t', namespaces=ns)
            text = "".join([t.text or "" for t in t_nodes]).strip()
            if len(text) >= 5:  # 過濾過短或空白行
                paragraphs.append(text)

    print(f"[*] 成功讀取 {len(paragraphs)} 個段落，開始離線使用 {args.model} 逐段審查...")

    comments = []
    for i, p_text in enumerate(paragraphs, 1):
        if len(p_text) > 800:
            chunks = [p_text[j:j+500] for j in range(0, len(p_text), 450)]
        else:
            chunks = [p_text]

        for chunk in chunks:
            prompt = f"""你是一位嚴謹的繁體中文（臺灣）學術與教育命題校對員。
請檢查以下文字是否有：
1. 錯別字（如：做答/作答、在/再、稱加/增加）
2. 標點符號錯誤（如：重複句號「。。」、全半形混用）
3. 非正式用語調整（將「孩子」改為「學生」、「老師」改為「教師」、「亂答/瞎猜」改為「任意作答」）
4. 特殊相容字元錯誤（如將特殊編碼「力」改為標準漢字「力」）

文字內容：
「{chunk}」

若有發現錯誤，請輸出 JSON 格式如下，完全不要包含 markdown 標籤或多餘寒暄：
{{
  "issues": [
    {{
      "contains": "原文中完全吻合的5~15字詞作為座標",
      "comment": "建議說明（繁體中文）"
    }}
  ]
}}
若完全無錯誤，請只輸出：{{"issues": []}}
"""
            res = call_ollama(prompt, model=args.model, base_url=args.url).strip()
            if "```json" in res:
                res = res.split("```json")[1].split("```")[0].strip()
            elif "```" in res:
                res = res.split("```")[1].split("```")[0].strip()

            try:
                data = json.loads(res)
                for issue in data.get("issues", []):
                    c_text = issue.get("contains", "").strip()
                    c_msg = issue.get("comment", "").strip()
                    if c_text and c_msg and c_text in chunk:
                        comments.append({
                            "contains": c_text,
                            "comment": f"【離線校對】{c_msg}",
                            "author": f"Ollama ({args.model})"
                        })
            except Exception:
                pass

        if i % 10 == 0 or i == len(paragraphs):
            print(f"    - 進度：{i}/{len(paragraphs)} 段完成，目前累積 {len(comments)} 個建議點")

    # 2. 產出 spec.json 並寫入 Word
    spec_json = { "comments": comments }
    temp_spec = input_path + ".temp_spec.json"
    with open(temp_spec, "w", encoding="utf-8") as f:
        json.dump(spec_json, f, ensure_ascii=False, indent=2)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    writer_script = os.path.join(script_dir, "add_comments_lxml.py")

    print(f"[*] 正在將 {len(comments)} 筆批註無損寫入 Word：{out_path}")
    subprocess.run([sys.executable, writer_script, input_path, out_path, temp_spec])

    if os.path.exists(temp_spec):
        os.remove(temp_spec)

    print(f"[✔] 離線校對完成！成果已存入：{out_path}")

if __name__ == "__main__":
    main()
