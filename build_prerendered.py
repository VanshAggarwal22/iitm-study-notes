import os
import re
import html

def md_to_clean_html(md_text):
    lines = md_text.split('\n')
    out = []
    
    in_code = False
    code_lang = ''
    code_lines = []
    
    in_table = False
    table_rows = []
    
    in_list = False
    
    for line in lines:
        # Check code fence
        if line.strip().startswith('```'):
            if not in_code:
                in_code = True
                code_lang = line.strip().lstrip('`').strip()
                code_lines = []
                continue
            else:
                in_code = False
                escaped = html.escape('\n'.join(code_lines))
                out.append(f'''<div class="code-wrap">
                    <div class="code-header"><span>{code_lang or "text"}</span><button class="copy-btn" onclick="navigator.clipboard.writeText(this.closest('.code-wrap').querySelector('code').innerText); this.innerText='Copied!'; setTimeout(()=>this.innerText='Copy',1500)">Copy</button></div>
                    <pre><code class="language-{code_lang}">{escaped}</code></pre>
                </div>''')
                continue
        
        if in_code:
            code_lines.append(line)
            continue
            
        # Table handling
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line.strip())
            continue
        else:
            if in_table:
                in_table = False
                # render table
                if len(table_rows) >= 2:
                    h_cols = [c.strip() for c in table_rows[0].strip('|').split('|')]
                    t_html = '<div class="table-container"><table><thead><tr>'
                    for c in h_cols:
                        t_html += f'<th>{c}</th>'
                    t_html += '</tr></thead><tbody>'
                    for r in table_rows[2:]:
                        r_cols = [c.strip() for c in r.strip('|').split('|')]
                        t_html += '<tr>'
                        for c in r_cols:
                            t_html += f'<td>{c}</td>'
                        t_html += '</tr>'
                    t_html += '</tbody></table></div>'
                    out.append(t_html)
                table_rows = []
        
        # Check list
        list_match = re.match(r'^\s*[\*\-]\s+(.+)$', line)
        if list_match:
            if not in_list:
                in_list = True
                out.append('<ul>')
            item_text = list_match.group(1)
            # format inline
            item_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item_text)
            item_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', item_text)
            out.append(f'<li>{item_text}</li>')
            continue
        else:
            if in_list:
                in_list = False
                out.append('</ul>')
        
        # Blank line
        if not line.strip():
            continue
            
        # Headers
        h_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if h_match:
            depth = len(h_match.group(1))
            h_text = h_match.group(2).strip()
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', h_text.lower()).strip('-')
            # format bold in header if any
            h_text = re.sub(r'\*\*(.+?)\*\*', r'\1', h_text)
            out.append(f'<h{depth} id="{slug}"><a href="#{slug}" class="anchor-link">#</a> {h_text}</h{depth}>')
            continue
            
        # Alerts / Blockquotes
        if line.strip().startswith('>'):
            bq_text = line.strip().lstrip('>').strip()
            if '[!IMPORTANT]' in bq_text:
                out.append(f'<div class="alert alert-important"><div class="alert-title">IMPORTANT</div>')
            elif '[!TIP]' in bq_text:
                out.append(f'<div class="alert alert-tip"><div class="alert-title">TIP</div>')
            elif '[!CAUTION]' in bq_text:
                out.append(f'<div class="alert alert-caution"><div class="alert-title">CAUTION</div>')
            elif bq_text.endswith('</div>'):
                out.append(bq_text)
            else:
                bq_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', bq_text)
                bq_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', bq_text)
                out.append(f'<blockquote>{bq_text}</blockquote>')
            continue
            
        # Horizontal rule
        if line.strip() in ['---', '***', '___']:
            out.append('<hr>')
            continue
            
        # Standard paragraph
        p_text = line.strip()
        p_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p_text)
        p_text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', p_text)
        p_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', p_text)
        out.append(f'<p>{p_text}</p>')
        
    if in_list:
        out.append('</ul>')
    if in_table and len(table_rows) >= 2:
        h_cols = [c.strip() for c in table_rows[0].strip('|').split('|')]
        t_html = '<div class="table-container"><table><thead><tr>'
        for c in h_cols:
            t_html += f'<th>{c}</th>'
        t_html += '</tr></thead><tbody>'
        for r in table_rows[2:]:
            r_cols = [c.strip() for c in r.strip('|').split('|')]
            t_html += '<tr>'
            for c in r_cols:
                t_html += f'<td>{c}</td>'
            t_html += '</tr>'
        t_html += '</tbody></table></div>'
        out.append(t_html)
        
    return '\n'.join(out)

md_file = "/Users/vansh/.gemini/antigravity/brain/facb67a6-0b3a-4de7-beb0-28a7b66ec42c/IITM_Quiz_1_Complete_Crash_Course_Notes.md"
with open(md_file, 'r', encoding='utf-8') as f:
    raw_markdown = f.read()

rendered_content = md_to_clean_html(raw_markdown)

# Build TOC
headers = []
for line in raw_markdown.split('\n'):
    m = re.match(r'^(#{1,3})\s+(.+)$', line)
    if m:
        level = len(m.group(1))
        title = m.group(2).strip()
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
        headers.append((level, title, slug))

toc_html = '<div class="toc-list">'
for level, title, slug in headers:
    clean_title = re.sub(r'\*\*(.+?)\*\*', r'\1', title)
    if level == 1:
        toc_html += f'<a href="#{slug}" class="toc-item toc-h1">{clean_title}</a>'
    elif level == 2:
        toc_html += f'<a href="#{slug}" class="toc-item toc-h2">{clean_title}</a>'
    elif level == 3:
        toc_html += f'<a href="#{slug}" class="toc-item toc-h3">{clean_title}</a>'
toc_html += '</div>'

full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>IIT Madras BS Degree — Quiz 1 Crash Course</title>
    
    <!-- KaTeX -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}, {{left: '\\\\(', right: '\\\\)', display: false}}]}});"></script>

    <!-- Prism Code Highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>

    <style>
        :root {{
            --bg: #0b0f19;
            --surface: #111827;
            --surface-card: #1e293b;
            --border: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #38bdf8;
            --code-bg: #090d16;
            --danger: #f87171;
            --warning: #fbbf24;
            --success: #34d399;
        }}
        [data-theme="light"] {{
            --bg: #ffffff;
            --surface: #f8fafc;
            --surface-card: #f1f5f9;
            --border: #cbd5e1;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --accent: #0284c7;
            --code-bg: #1e293b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-primary);
            line-height: 1.7;
            -webkit-font-smoothing: antialiased;
            padding-bottom: 90px;
        }}
        #progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 4px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            width: 0%;
            z-index: 1000;
        }}
        header.nav-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(16px);
            background: rgba(11, 15, 25, 0.92);
            border-bottom: 1px solid var(--border);
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        [data-theme="light"] header.nav-header {{
            background: rgba(255, 255, 255, 0.92);
        }}
        .header-title {{
            font-size: 1rem;
            font-weight: 700;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .header-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .btn {{
            background: var(--surface-card);
            color: var(--text-primary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 7px 14px;
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .layout {{
            max-width: 900px;
            margin: 0 auto;
            padding: 24px 18px;
        }}
        h1 {{
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.3;
            margin: 32px 0 16px;
            color: #ffffff;
            border-bottom: 2px solid var(--accent);
            padding-bottom: 8px;
        }}
        [data-theme="light"] h1 {{ color: #0f172a; }}
        h2 {{
            font-size: 1.4rem;
            font-weight: 700;
            margin: 38px 0 14px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border);
            color: var(--accent);
        }}
        h3 {{
            font-size: 1.15rem;
            font-weight: 600;
            margin: 26px 0 10px;
            color: #f1f5f9;
        }}
        [data-theme="light"] h3 {{ color: #1e293b; }}
        p {{ margin-bottom: 14px; font-size: 1rem; }}
        hr {{ border: 0; height: 1px; background: var(--border); margin: 28px 0; }}
        .anchor-link {{
            opacity: 0.35;
            text-decoration: none;
            color: inherit;
            margin-right: 6px;
        }}
        .anchor-link:hover {{ opacity: 1; }}
        .table-container {{
            width: 100%;
            overflow-x: auto;
            margin: 20px 0;
            border-radius: 8px;
            border: 1px solid var(--border);
            -webkit-overflow-scrolling: touch;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.92rem;
            text-align: left;
        }}
        th, td {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: var(--surface-card);
            color: var(--accent);
            font-weight: 600;
        }}
        tr:last-child td {{ border-bottom: none; }}
        .code-wrap {{
            margin: 18px 0;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border);
            background: var(--code-bg);
        }}
        .code-header {{
            background: #161f30;
            padding: 6px 14px;
            font-size: 0.78rem;
            font-family: monospace;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}
        .copy-btn {{
            background: rgba(255,255,255,0.12);
            border: none;
            color: #f8fafc;
            padding: 3px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.75rem;
        }}
        pre {{
            margin: 0;
            padding: 14px;
            overflow-x: auto;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.88rem;
            line-height: 1.55;
            background: transparent !important;
        }}
        code:not(pre code) {{
            background: var(--surface-card);
            color: var(--accent);
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.9em;
            padding: 2px 6px;
            border-radius: 5px;
            border: 1px solid var(--border);
        }}
        ul, ol {{ margin-left: 24px; margin-bottom: 16px; }}
        li {{ margin-bottom: 6px; }}
        blockquote {{
            border-left: 4px solid var(--accent);
            padding: 10px 16px;
            margin: 16px 0;
            background: rgba(56, 189, 248, 0.08);
            border-radius: 0 8px 8px 0;
        }}
        .alert {{
            padding: 14px 16px;
            border-radius: 10px;
            margin: 18px 0;
            border-left: 4px solid;
            font-size: 0.95rem;
        }}
        .alert-title {{ font-weight: 700; font-size: 0.82rem; margin-bottom: 4px; }}
        .alert-important {{ background: rgba(248, 113, 113, 0.12); border-color: var(--danger); color: #fecaca; }}
        [data-theme="light"] .alert-important {{ color: #991b1b; }}
        .alert-tip {{ background: rgba(56, 189, 248, 0.12); border-color: var(--accent); color: #bae6fd; }}
        [data-theme="light"] .alert-tip {{ color: #075985; }}
        .alert-caution {{ background: rgba(251, 191, 36, 0.12); border-color: var(--warning); color: #fde68a; }}
        [data-theme="light"] .alert-caution {{ color: #92400e; }}
        
        #toc-drawer {{
            display: none;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            top: 56px;
            background: var(--bg);
            z-index: 200;
            padding: 24px 20px;
            overflow-y: auto;
            border-top: 1px solid var(--border);
        }}
        .toc-list {{ display: flex; flex-direction: column; gap: 8px; }}
        .toc-item {{
            color: var(--text-secondary);
            text-decoration: none;
            padding: 6px 0;
            border-radius: 6px;
        }}
        .toc-item:hover {{ color: var(--accent); }}
        .toc-h1 {{ font-weight: 700; color: var(--text-primary); margin-top: 10px; font-size: 1rem; }}
        .toc-h2 {{ padding-left: 14px; font-size: 0.92rem; }}
        .toc-h3 {{ padding-left: 28px; font-size: 0.85rem; }}
        
        .fab-toc {{
            position: fixed;
            bottom: 24px;
            right: 20px;
            background: var(--accent);
            color: #0b0f19;
            font-weight: 700;
            padding: 12px 22px;
            border-radius: 30px;
            border: none;
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.45);
            cursor: pointer;
            z-index: 150;
            font-size: 0.92rem;
        }}
        .search-box {{
            width: 100%;
            padding: 12px 14px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.92rem;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div id="progress-bar"></div>
    <header class="nav-header">
        <div class="header-title">
            <span>📚</span>
            <span>IITM Quiz 1 Master Notes</span>
        </div>
        <div class="header-actions">
            <button class="btn" onclick="toggleTheme()" id="theme-btn">🌓 Theme</button>
            <button class="btn" onclick="toggleTOC()">📑 Topics</button>
        </div>
    </header>

    <div id="toc-drawer">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px;">
            <h3 style="margin:0;">Table of Contents</h3>
            <button class="btn" onclick="toggleTOC()">✕ Close</button>
        </div>
        <input type="text" id="toc-search" placeholder="Search headings..." class="search-box" oninput="filterTOC()">
        {toc_html}
    </div>

    <main class="layout">
        <!-- PURE STATIC PRE-RENDERED CONTENT -->
        {rendered_content}
    </main>

    <button class="fab-toc" onclick="toggleTOC()">
        📑 Jump to Topic
    </button>

    <script>
        // Reading Progress
        window.addEventListener('scroll', () => {{
            const winScroll = document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            document.getElementById('progress-bar').style.width = scrolled + '%';
        }});

        // Theme toggle
        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('notes-theme', target);
        }}
        const savedTheme = localStorage.getItem('notes-theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);

        // TOC Toggle
        function toggleTOC() {{
            const d = document.getElementById('toc-drawer');
            d.style.display = (d.style.display === 'block') ? 'none' : 'block';
        }}
        function filterTOC() {{
            const q = document.getElementById('toc-search').value.toLowerCase();
            document.querySelectorAll('.toc-item').forEach(el => {{
                el.style.display = el.innerText.toLowerCase().includes(q) ? 'block' : 'none';
            }});
        }}
        document.querySelectorAll('.toc-item').forEach(el => {{
            el.addEventListener('click', () => {{
                document.getElementById('toc-drawer').style.display = 'none';
            }});
        }});
    </script>
</body>
</html>'''

with open('/tmp/iitm-notes-site/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print("Pre-rendered static index.html built successfully! Size:", len(full_html))
