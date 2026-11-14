import os
import re
import html
import subprocess

def convert_md_to_html(md_path, title="IIT Madras BS Degree — Quiz 1 Crash Course"):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Escape raw HTML inside code blocks first
    code_blocks = []
    def code_repl(match):
        lang = match.group(1) or 'bash'
        code = match.group(2)
        code_blocks.append((lang, code))
        return f"<!--CODE_BLOCK_{len(code_blocks)-1}-->"
    
    content = re.sub(r'```([a-zA-Z0-9_\-\+]*)\n(.*?)```', code_repl, content, flags=re.DOTALL)

    # Convert KaTeX display math $$...$$
    math_blocks = []
    def math_block_repl(match):
        math_blocks.append(match.group(1))
        return f"<!--MATH_BLOCK_{len(math_blocks)-1}-->"
    content = re.sub(r'\$\$(.*?)\$\$', math_block_repl, content, flags=re.DOTALL)

    # Convert KaTeX inline math $...$
    math_inlines = []
    def math_inline_repl(match):
        math_inlines.append(match.group(1))
        return f"<!--MATH_INLINE_{len(math_inlines)-1}-->"
    content = re.sub(r'\$(.*?)\$', math_inline_repl, content)

    # Convert markdown elements
    # Headers
    headers = []
    def header_repl(match):
        level = len(match.group(1))
        text = match.group(2).strip()
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')
        headers.append((level, text, slug))
        return f'<h{level} id="{slug}"><a href="#{slug}" class="anchor-link">#</a> {text}</h{level}>'
    content = re.sub(r'^(#{1,4})\s+(.+)$', header_repl, content, flags=re.MULTILINE)

    # Tables
    def parse_table(match):
        rows = match.group(0).strip().split('\n')
        if len(rows) < 2:
            return match.group(0)
        header_cols = [c.strip() for c in rows[0].strip('|').split('|')]
        html_out = '<div class="table-container"><table><thead><tr>'
        for col in header_cols:
            html_out += f'<th>{col}</th>'
        html_out += '</tr></thead><tbody>'
        for row in rows[2:]:
            cols = [c.strip() for c in row.strip('|').split('|')]
            html_out += '<tr>'
            for col in cols:
                html_out += f'<td>{col}</td>'
            html_out += '</tr>'
        html_out += '</tbody></table></div>'
        return html_out
    
    content = re.sub(r'(\|.+?\|\n\|[-:\s|]+?\|\n(?:\|.+?\|\n*)+)', parse_table, content)

    # Blockquotes / Alerts
    content = re.sub(r'>\s*\[!IMPORTANT\]\s*(.*?)(?=\n\n|\n[^\>]|$)', r'<div class="alert alert-important"><div class="alert-title">IMPORTANT</div>\1</div>', content, flags=re.DOTALL)
    content = re.sub(r'>\s*\[!TIP\]\s*(.*?)(?=\n\n|\n[^\>]|$)', r'<div class="alert alert-tip"><div class="alert-title">TIP</div>\1</div>', content, flags=re.DOTALL)
    content = re.sub(r'>\s*\[!CAUTION\]\s*(.*?)(?=\n\n|\n[^\>]|$)', r'<div class="alert alert-caution"><div class="alert-title">CAUTION</div>\1</div>', content, flags=re.DOTALL)
    content = re.sub(r'>\s*(.*?)(?=\n\n|\n[^\>]|$)', r'<blockquote>\1</blockquote>', content, flags=re.DOTALL)

    # Bold and italics
    content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)

    # Inline code `...`
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)

    # Unordered Lists
    lines = content.split('\n')
    in_list = False
    new_lines = []
    for line in lines:
        m = re.match(r'^\s*[\*\-]\s+(.+)$', line)
        if m:
            if not in_list:
                new_lines.append('<ul>')
                in_list = True
            new_lines.append(f'<li>{m.group(1)}</li>')
        else:
            if in_list and line.strip() == '':
                continue
            elif in_list:
                new_lines.append('</ul>')
                in_list = False
            new_lines.append(line)
    if in_list:
        new_lines.append('</ul>')
    content = '\n'.join(new_lines)

    # Paragraphs
    blocks = content.split('\n\n')
    parsed_blocks = []
    for b in blocks:
        b_str = b.strip()
        if not b_str:
            continue
        if any(b_str.startswith(tag) for tag in ['<h', '<div', '<table', '<ul', '<ol', '<blockquote', '<!--']):
            parsed_blocks.append(b_str)
        else:
            parsed_blocks.append(f'<p>{b_str.replace(chr(10), "<br>")}</p>')
    content = '\n\n'.join(parsed_blocks)

    # Restore code blocks
    for idx, (lang, code) in enumerate(code_blocks):
        escaped_code = html.escape(code.strip())
        code_html = f'''<div class="code-wrap">
            <div class="code-header">
                <span class="code-lang">{lang or "text"}</span>
                <button class="copy-btn" onclick="navigator.clipboard.writeText(this.closest('.code-wrap').querySelector('code').innerText); this.innerText='Copied!'; setTimeout(()=>this.innerText='Copy', 1500)">Copy</button>
            </div>
            <pre><code class="language-{lang}">{escaped_code}</code></pre>
        </div>'''
        content = content.replace(f"<!--CODE_BLOCK_{idx}-->", code_html)

    # Restore math blocks
    for idx, m in enumerate(math_blocks):
        m_esc = html.escape(m)
        content = content.replace(f"<!--MATH_BLOCK_{idx}-->", f'<div class="math-display">\\({m_esc}\\)</div>')

    for idx, m in enumerate(math_inlines):
        m_esc = html.escape(m)
        content = content.replace(f"<!--MATH_INLINE_{idx}-->", f'<span class="math-inline">\\({m_esc}\\)</span>')

    # Build TOC HTML
    toc_html = '<div class="toc-list">'
    for level, text, slug in headers:
        if level in [1, 2]:
            pad = 'pl-2 font-bold' if level == 1 else 'pl-4 text-sm'
            toc_html += f'<a href="#{slug}" class="toc-item {pad}">{html.escape(text)}</a>'
    toc_html += '</div>'

    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <!-- Google Fonts & KaTeX -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '\\(', right: '\\)', display: false}}]}});"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js"></script>
    <style>
        :root {{
            --bg: #0b0f19;
            --surface: #111827;
            --surface-card: #1f2937;
            --border: #374151;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --code-bg: #090d16;
            --success: #34d399;
            --warning: #fbbf24;
            --danger: #f87171;
        }}
        [data-theme="light"] {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --surface-card: #f1f5f9;
            --border: #e2e8f0;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --accent: #0284c7;
            --accent-glow: rgba(2, 132, 199, 0.1);
            --code-bg: #1e293b;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text-primary);
            line-height: 1.65;
            -webkit-font-smoothing: antialiased;
            padding-bottom: 80px;
        }}
        #progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            width: 0%;
            z-index: 999;
            transition: width 0.1s;
        }}
        header.nav-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(16px);
            background: rgba(11, 15, 25, 0.85);
            border-bottom: 1px solid var(--border);
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        [data-theme="light"] header.nav-header {{
            background: rgba(248, 250, 252, 0.85);
        }}
        .header-title {{
            font-size: 0.95rem;
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
            padding: 6px 12px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s;
        }}
        .btn:hover {{ border-color: var(--accent); }}
        .layout {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px 16px;
        }}
        h1 {{
            font-size: 1.75rem;
            font-weight: 800;
            line-height: 1.25;
            margin: 24px 0 16px;
            letter-spacing: -0.025em;
            color: #fff;
        }}
        [data-theme="light"] h1 {{ color: #0f172a; }}
        h2 {{
            font-size: 1.35rem;
            font-weight: 700;
            margin: 36px 0 14px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border);
            color: var(--accent);
        }}
        h3 {{
            font-size: 1.1rem;
            font-weight: 600;
            margin: 24px 0 10px;
            color: #e2e8f0;
        }}
        [data-theme="light"] h3 {{ color: #1e293b; }}
        p {{ margin-bottom: 14px; color: var(--text-primary); }}
        .anchor-link {{
            opacity: 0.3;
            text-decoration: none;
            color: inherit;
            margin-right: 4px;
        }}
        .anchor-link:hover {{ opacity: 1; }}
        .table-container {{
            width: 100%;
            overflow-x: auto;
            margin: 16px 0;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--surface);
            -webkit-overflow-scrolling: touch;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            text-align: left;
        }}
        th, td {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: var(--surface-card);
            font-weight: 600;
            color: var(--accent);
        }}
        tr:last-child td {{ border-bottom: none; }}
        .code-wrap {{
            margin: 16px 0;
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border);
            background: var(--code-bg);
        }}
        .code-header {{
            background: #161f30;
            padding: 6px 14px;
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
            color: var(--text-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }}
        .copy-btn {{
            background: rgba(255,255,255,0.08);
            border: none;
            color: #cbd5e1;
            padding: 2px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.72rem;
        }}
        pre {{
            margin: 0;
            padding: 14px;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.5;
        }}
        code:not(pre code) {{
            background: var(--surface-card);
            color: var(--accent);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.88em;
            padding: 2px 6px;
            border-radius: 5px;
            border: 1px solid var(--border);
        }}
        ul, ol {{
            margin-left: 20px;
            margin-bottom: 16px;
        }}
        li {{ margin-bottom: 6px; }}
        .alert {{
            padding: 14px 16px;
            border-radius: 10px;
            margin: 18px 0;
            border-left: 4px solid;
            font-size: 0.92rem;
        }}
        .alert-title {{
            font-weight: 700;
            font-size: 0.8rem;
            margin-bottom: 4px;
            letter-spacing: 0.05em;
        }}
        .alert-important {{
            background: rgba(248, 113, 113, 0.1);
            border-color: var(--danger);
            color: #fecaca;
        }}
        [data-theme="light"] .alert-important {{ color: #991b1b; }}
        .alert-tip {{
            background: rgba(56, 189, 248, 0.1);
            border-color: var(--accent);
            color: #bae6fd;
        }}
        [data-theme="light"] .alert-tip {{ color: #075985; }}
        .alert-caution {{
            background: rgba(251, 191, 36, 0.1);
            border-color: var(--warning);
            color: #fde68a;
        }}
        [data-theme="light"] .alert-caution {{ color: #92400e; }}
        .math-display {{
            overflow-x: auto;
            padding: 12px 0;
            text-align: center;
        }}
        /* Drawer for TOC */
        #toc-drawer {{
            display: none;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            top: 60px;
            background: var(--bg);
            z-index: 200;
            padding: 20px;
            overflow-y: auto;
            border-top: 1px solid var(--border);
        }}
        .toc-list {{ display: flex; flex-direction: column; gap: 8px; }}
        .toc-item {{
            color: var(--text-secondary);
            text-decoration: none;
            padding: 6px 0;
            border-radius: 6px;
            transition: color 0.15s;
        }}
        .toc-item:hover {{ color: var(--accent); }}
        .pl-2 {{ padding-left: 8px; }}
        .pl-4 {{ padding-left: 20px; }}
        .text-sm {{ font-size: 0.85rem; }}
        .font-bold {{ font-weight: 600; color: var(--text-primary); }}
        .fab-toc {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--accent);
            color: #0b0f19;
            font-weight: 700;
            padding: 12px 18px;
            border-radius: 30px;
            border: none;
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.4);
            cursor: pointer;
            z-index: 150;
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
        }}
        .search-box {{
            width: 100%;
            padding: 10px 14px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.9rem;
            margin-bottom: 20px;
        }}
        .search-box:focus {{ outline: 2px solid var(--accent); }}
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
            <button class="btn" onclick="toggleTheme()" id="theme-btn">🌓</button>
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
        {content}
    </main>

    <button class="fab-toc" onclick="toggleTOC()">
        📑 Jump to Topic
    </button>

    <script>
        // Progress bar
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

    return html_template

if __name__ == '__main__':
    md_file = "/Users/vansh/.gemini/antigravity/brain/facb67a6-0b3a-4de7-beb0-28a7b66ec42c/IITM_Quiz_1_Complete_Crash_Course_Notes.md"
    out_html = "/tmp/iitm-notes-site/index.html"
    print("Converting markdown to mobile HTML...")
    rendered = convert_md_to_html(md_file)
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(rendered)
    print("Done! Output at", out_html)
