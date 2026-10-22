#!/usr/bin/env python3
"""Renders an HTML report the way a reader sees it and writes it as text.

Reports built with JavaScript (numbers filled in from embedded JSON) show nothing useful in their source, so the
page is loaded in headless Chrome first; without Chrome the script strips the static HTML and says so. Tables keep
their rows (one line per row, cells separated by " | ") so a validator can quote a cell and its row.

  python3 render_report.py <report.html> [--out <rendered.txt>] [--wait-ms 8000]

Also writes <out>.meta.json: how it was rendered, sizes, and the headings found (the page outline).
"""
import argparse, html, json, os, re, shutil, subprocess, sys, tempfile

CHROME = [
    os.environ.get('CHROME_BIN', ''),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    shutil.which('google-chrome') or '', shutil.which('chromium') or '', shutil.which('chromium-browser') or '',
]

def render_dom(path, wait_ms):
    for exe in CHROME:
        if exe and os.path.exists(exe):
            with tempfile.TemporaryDirectory(prefix='report-render-') as prof:
                cmd = [exe, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={prof}',
                       f'--virtual-time-budget={wait_ms}', '--dump-dom', 'file://' + os.path.abspath(path)]
                try:
                    out = subprocess.run(cmd, capture_output=True, text=True, timeout=180).stdout
                except subprocess.TimeoutExpired:
                    out = ''
            if out.strip():
                return out, f'headless Chrome ({os.path.basename(exe)}), virtual time {wait_ms} ms'
    return open(path, encoding='utf-8', errors='replace').read(), 'static source only: no Chrome found, JavaScript did NOT run'

def to_text(dom):
    t = re.sub(r'<(script|style|noscript|svg|canvas)\b.*?</\1>', ' ', dom, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<(br|hr)\s*/?>', '\n', t, flags=re.I)
    t = re.sub(r'</t[hd]>', ' | ', t, flags=re.I)
    t = re.sub(r'</tr>', '\n', t, flags=re.I)
    t = re.sub(r'<(h[1-6])\b[^>]*>', lambda m: '\n' + '#' * int(m.group(1)[1]) + ' ', t, flags=re.I)
    t = re.sub(r'</h[1-6]>', '\n', t, flags=re.I)
    t = re.sub(r'<(?:/?(?:p|div|li|ul|ol|section|article|header|footer|table|thead|tbody|tr|details|summary|dl|dt|dd|pre|blockquote|figure|figcaption|nav|aside|main))\b[^>]*>', '\n', t, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t).replace('\xa0', ' ')
    lines = [re.sub(r'[ \t]+', ' ', l).strip(' |') for l in t.split('\n')]
    lines = [l for l in lines if l]
    out, prev = [], None
    for l in lines:  # collapse exact duplicates that come from nested block tags
        if l != prev: out.append(l)
        prev = l
    return '\n'.join(out) + '\n'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report'); ap.add_argument('--out'); ap.add_argument('--wait-ms', type=int, default=8000)
    a = ap.parse_args()
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.report)), 'validation', 'rendered.txt')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    dom, how = render_dom(a.report, a.wait_ms)
    text = to_text(dom)
    open(out, 'w', encoding='utf-8').write(text)
    headings = [l for l in text.split('\n') if l.startswith('#')]
    suspicious = sorted({w for w in re.findall(r'\b(?:NaN|undefined|null|Infinity|\[object Object\])\b', text)})
    meta = {'report': os.path.abspath(a.report), 'rendered_with': how, 'dom_bytes': len(dom), 'text_chars': len(text),
            'lines': text.count('\n'), 'headings': headings[:80], 'suspicious_tokens': suspicious}
    json.dump(meta, open(out + '.meta.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: meta[k] for k in ('rendered_with', 'text_chars', 'lines', 'suspicious_tokens')}, ensure_ascii=False))
    print('rendered text:', out)

if __name__ == '__main__':
    main()
