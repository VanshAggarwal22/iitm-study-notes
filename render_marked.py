import json
import re

md_file = "/Users/vansh/.gemini/antigravity/brain/facb67a6-0b3a-4de7-beb0-28a7b66ec42c/IITM_Quiz_1_Complete_Crash_Course_Notes.md"
with open(md_file, 'r', encoding='utf-8') as f:
    raw_markdown = f.read()

# Generate TOC headings from markdown
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
    if level == 1:
        toc_html += f'<a href="#{slug}" class="toc-item toc-h1">{title}</a>'
    elif level == 2:
        toc_html += f'<a href="#{slug}" class="toc-item toc-h2">{title}</a>'
    elif level == 3:
        toc_html += f'<a href="#{slug}" class="toc-item toc-h3">{title}</a>'
toc_html += '</div>'

html_page = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>IIT Madras BS Degree — Quiz 1 Crash Course (SE2001 & CS2001)</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    
    <!-- KaTeX -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>

    <!-- Marked.js -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

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
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --code-bg: #090d16;
            --danger: #f87171;
            --warning: #fbbf24;
            --success: #34d399;
        }}
        [data-theme="light"] {{
            --bg: #f8fafc;
            --surface: #ffffff;
            --surface-card: #f1f5f9;
            --border: #cbd5e1;
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
            line-height: 1.7;
            -webkit-font-smoothing: antialiased;
            padding-bottom: 90px;
        }}
        #progress-bar {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            width: 0%;
            z-index: 1000;
            transition: width 0.1s;
        }}
        header.nav-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(16px);
            background: rgba(11, 15, 25, 0.9);
            border-bottom: 1px solid var(--border);
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        [data-theme="light"] header.nav-header {{
            background: rgba(248, 250, 252, 0.9);
        }}
        .header-title {{
            font-size: 0.98rem;
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
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s;
        }}
        .btn:hover {{ border-color: var(--accent); }}
        .layout {{
            max-width: 900px;
            margin: 0 auto;
            padding: 24px 18px;
        }}
        h1 {{
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.25;
            margin: 28px 0 16px;
            letter-spacing: -0.025em;
            color: #fff;
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
            color: #e2e8f0;
        }}
        [data-theme="light"] h3 {{ color: #1e293b; }}
        p {{ margin-bottom: 14px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            margin: 18px 0;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        th, td {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            text-align: left;
        }}
        th {{
            background: var(--surface-card);
            color: var(--accent);
            font-weight: 600;
        }}
        pre {{
            margin: 16px 0;
            padding: 14px;
            border-radius: 10px;
            background: var(--code-bg) !important;
            border: 1px solid var(--border);
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
        ul, ol {{ margin-left: 24px; margin-bottom: 16px; }}
        li {{ margin-bottom: 6px; }}
        blockquote {{
            border-left: 4px solid var(--accent);
            padding: 10px 16px;
            margin: 16px 0;
            background: rgba(56, 189, 248, 0.08);
            border-radius: 0 8px 8px 0;
        }}
        /* Drawer for TOC */
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
            transition: color 0.15s;
        }}
        .toc-item:hover {{ color: var(--accent); }}
        .toc-h1 {{ font-weight: 700; color: var(--text-primary); margin-top: 10px; font-size: 0.98rem; }}
        .toc-h2 {{ padding-left: 14px; font-size: 0.9rem; }}
        .toc-h3 {{ padding-left: 28px; font-size: 0.84rem; }}
        .fab-toc {{
            position: fixed;
            bottom: 24px;
            right: 20px;
            background: var(--accent);
            color: #0b0f19;
            font-weight: 700;
            padding: 12px 20px;
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
            padding: 12px 14px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.92rem;
            margin-bottom: 20px;
        }}
        .search-box:focus {{ outline: 2px solid var(--accent); }}
        .math-display {{ overflow-x: auto; padding: 10px 0; }}
    </style>
</head>
<body>
    <div id="progress-bar"></div>
    <header class="nav-header">
        <div class="header-title">
            <span>📚</span>
            <span>IITM Quiz 1 Notes</span>
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

    <main class="layout" id="markdown-container">
        <!-- Rendered markdown injected here -->
        <div style="text-align:center; padding: 40px; color: var(--text-secondary);">Loading notes...</div>
    </main>

    <button class="fab-toc" onclick="toggleTOC()">
        📑 Jump to Topic
    </button>

    <script id="raw-markdown" type="text/plain">{json.dumps(raw_markdown)}</script>

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

        // Render Markdown with marked.js
        window.addEventListener('DOMContentLoaded', () => {{
            const raw = JSON.parse(document.getElementById('raw-markdown').textContent);
            
            // Custom heading renderer to include slug IDs
            const renderer = new marked.Renderer();
            renderer.heading = function({{ text, depth }}) {{
                const clean = text.replace(/<[^>]+>/g, '').trim();
                const slug = clean.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
                return `<h${{depth}} id="${{slug}}"><a href="#${{slug}}" style="opacity:0.3; text-decoration:none; color:inherit; margin-right:6px;">#</a>${{text}}</h${{depth}}>`;
            }};
            
            marked.use({{ renderer }});
            document.getElementById('markdown-container').innerHTML = marked.parse(raw);

            // Re-render KaTeX math
            if (window.renderMathInElement) {{
                renderMathInElement(document.getElementById('markdown-container'), {{
                    delimiters: [
                        {{left: '$$', right: '$$', display: true}},
                        {{left: '$', right: '$', display: false}},
                        {{left: '\\\\(', right: '\\\\)', display: false}},
                        {{left: '\\\\[', right: '\\\\]', display: true}}
                    ],
                    throwOnError: false
                }});
            }}

            // Re-run Prism code highlighting
            if (window.Prism) {{
                Prism.highlightAll();
            }}
        }});
    </script>
</body>
</html>'''

with open('/tmp/iitm-notes-site/index.html', 'w', encoding='utf-8') as f:
    f.write(html_page)

print("Regenerated /tmp/iitm-notes-site/index.html successfully!")
