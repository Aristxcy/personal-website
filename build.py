#!/usr/bin/env python3
"""Build the static site from content/*.md. Usage: python3 build.py"""
import io
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

PAGES = [
    ('index.html', 'home', 'Home | Chenyu Xue', 'Personal academic homepage of Chenyu Xue.'),
    ('blogs.html', 'blogs', 'Blogs | Chenyu Xue', 'Blog notes of Chenyu Xue.'),
    ('research.html', 'research', 'Research | Chenyu Xue', 'Publications of Chenyu Xue.'),
    ('talks.html', 'talks', 'Talks | Chenyu Xue', 'Talks of Chenyu Xue.'),
    ('teaching.html', 'teaching', 'Teaching | Chenyu Xue', 'Teaching experience of Chenyu Xue.'),
    ('service.html', 'service', 'Service | Chenyu Xue', 'Academic service of Chenyu Xue.'),
]

NAV = [('index.html', 'Home'), ('blogs.html', 'Blogs'), ('research.html', 'Research'),
       ('talks.html', 'Talks'), ('teaching.html', 'Teaching'), ('service.html', 'Service')]

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="css/style.css">
<script>
window.MathJax = {{ tex: {{ inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] }} }};
</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>

<header class="site-header">
  <a class="site-title" href="index.html">Chenyu Xue</a>
  <nav class="site-nav" aria-label="Site">
{nav}
  </nav>
</header>

<main class="content">
{main}
</main>

<script src="js/toc.js"></script>
</body>
</html>
'''


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def inline(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]*)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    return s


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def parse(md):
    blocks = []
    lines = md.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip() or line.strip().startswith('<!--'):
            if line.strip().startswith('<!--'):
                while i < len(lines) and '-->' not in lines[i]:
                    i += 1
            i += 1
            continue
        if line.startswith('### '):
            blocks.append({'t': 'h3', 'text': line[4:].strip()})
            i += 1
        elif line.startswith('## '):
            blocks.append({'t': 'h2', 'text': line[3:].strip()})
            i += 1
        elif line.startswith('> '):
            blocks.append({'t': 'note', 'html': inline(line[2:].strip())})
            i += 1
        elif line.startswith('!['):
            m = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            blocks.append({'t': 'img', 'alt': m.group(1), 'src': m.group(2)})
            i += 1
        elif re.match(r'^\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i]):
                m = re.match(r'^(\d+)\.\s+(.*)$', lines[i].rstrip())
                item = {'num': int(m.group(1)), 'title': m.group(2).strip(), 'details': []}
                i += 1
                while i < len(lines) and re.match(r'^\s+-\s+', lines[i]):
                    item['details'].append(inline(re.match(r'^\s+-\s+(.*)$', lines[i].rstrip()).group(1)))
                    i += 1
                items.append(item)
            blocks.append({'t': 'ol', 'items': items})
        elif re.match(r'^-\s+', line):
            items = []
            while i < len(lines) and re.match(r'^-\s+', lines[i]):
                items.append(inline(re.match(r'^-\s+(.*)$', lines[i].rstrip()).group(1)))
                i += 1
            blocks.append({'t': 'ul', 'items': items})
        else:
            buf = [line.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'^(###\s|##\s|> |!\\[|\d+\. |- )', lines[i]):
                buf.append(lines[i].strip())
                i += 1
            blocks.append({'t': 'p', 'html': inline(' '.join(buf))})
    return blocks


def render(blocks, page_id):
    out = []
    toc = []
    pid = 0
    tid = 0
    for b in blocks:
        if b['t'] == 'h2':
            sid = slug(b['text'])
            out.append('<h2 id="%s">%s</h2>' % (sid, esc(b['text'])))
            toc.append({'id': sid, 'text': b['text']})
        elif b['t'] == 'h3':
            out.append('<h3>%s</h3>' % esc(b['text']))
        elif b['t'] == 'note':
            out.append('<p class="note">%s</p>' % b['html'])
        elif b['t'] == 'img':
            out.append('<img class="photo" src="%s" alt="%s">' % (esc(b['src']), esc(b['alt'])))
        elif b['t'] == 'p':
            out.append('<p>%s</p>' % b['html'])
        elif b['t'] == 'ol':
            start = ' start="%d"' % b['items'][0]['num'] if b['items'][0]['num'] != 1 else ''
            parts = ['<ol class="papers"%s>' % start]
            for item in b['items']:
                pid += 1
                anchor = 'p%d' % pid
                title_html = inline(item['title'])
                if title_html.startswith('<a '):
                    title_html = title_html.replace('<a ', '<a class="ptitle" ', 1)
                parts.append('<li id="%s"><p>%s</p>' % (anchor, title_html))
                if item['details']:
                    parts.append('<ul class="details">')
                    for d in item['details']:
                        parts.append('<li><p>%s</p></li>' % d)
                    parts.append('</ul>')
                parts.append('</li>')
            parts.append('</ol>')
            out.append('\n'.join(parts))
        elif b['t'] == 'ul':
            parts = ['<ul class="details flat">']
            for it in b['items']:
                tid += 1
                anchor = 't%d' % tid
                parts.append('<li id="%s"><p>%s</p></li>' % (anchor, it))
            parts.append('</ul>')
            out.append('\n'.join(parts))
    return '\n'.join(out), toc


def toc_html(toc):
    if len(toc) < 2:
        return ''
    parts = ['<nav class="toc-widget" aria-label="Contents">',
             '<div class="toc-panel" id="toc-panel">']
    for sec in toc:
        parts.append('<a href="#%s">%s</a>' % (sec['id'], esc(sec['text'])))
    parts.append('</div>')
    parts.append('<button class="toc-fab" type="button" aria-expanded="false" '
                 'aria-controls="toc-panel" aria-label="Contents">'
                 '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
                 '<path d="M4 6h16M4 12h16M4 18h10" stroke="currentColor" '
                 'stroke-width="2" stroke-linecap="round"/></svg></button>')
    parts.append('</nav>')
    return '\n'.join(parts)


def main():
    for fname, page_id, title, desc in PAGES:
        md = io.open(os.path.join(ROOT, 'content', page_id + '.md'), encoding='utf-8').read()
        blocks = parse(md)
        body, toc = render(blocks, page_id)
        if page_id == 'home':
            m = re.match(r'(<img[^>]*>)\s*(<p>.*?</p>)\s*(.*)', body, re.S)
            main_html = ('<div class="home-grid">\n<div class="home-left">\n%s\n%s\n</div>\n'
                         '<div class="home-right">\n%s\n</div>\n</div>'
                         % (m.group(1), m.group(2), m.group(3)))
        elif toc:
            main_html = '<div class="page-body">\n%s\n</div>\n%s' % (body, toc_html(toc))
        else:
            main_html = body
        nav = '\n'.join('    <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == fname else '', t) for h, t in NAV)
        html = TEMPLATE.format(title=title, desc=desc, nav=nav, main=main_html)
        io.open(os.path.join(ROOT, fname), 'w', encoding='utf-8').write(html)
        print('built', fname)


if __name__ == '__main__':
    main()
