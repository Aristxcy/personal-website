#!/usr/bin/env python3
"""Build the static site from content/*.md. Usage: python3 build.py"""
import datetime
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

<main class="content{mainclass}">
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
    s = re.sub(r'\*\[([^\]]*)\]\*\(([^)\s]+)\)', r'<em><a class="plain" href="\2">\1</a></em>', s)
    s = re.sub(r'_([^_]+)_', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]*)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'[A-Za-z0-9._]+ \[at\] [A-Za-z0-9._-]+(?: \[dot\] [A-Za-z0-9._-]+)*', r'<span class="nowrap">\g<0></span>', s)
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
        elif re.match(r'^\[\d+\]\s+', line) or re.match(r'^\d+\.\s+', line):
            items = []
            while i < len(lines) and (re.match(r'^\[\d+\]\s+', lines[i]) or re.match(r'^\d+\.\s+', lines[i])):
                m = re.match(r'^(?:\[(\d+)\]|(\d+)\.)\s+(.*)$', lines[i].rstrip())
                num = int(m.group(1) or m.group(2))
                item = {'num': num, 'bracket': m.group(1) is not None,
                        'title': m.group(3).strip(), 'details': []}
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
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#{2,3}\s|>\s|!\[|\[\d+\]\s|\d+\.\s|-\s)', lines[i]):
                buf.append(lines[i].strip())
                i += 1
            text = ' '.join(buf)
            cls = ' class="tldr"' if text.startswith('TL;DR:') else ''
            blocks.append({'t': 'p', 'html': inline(text), 'cls': cls})
    return blocks


def render(blocks, page_id):
    out = []
    toc = []
    ol_toc = []
    pid = 0
    tid = 0
    for b in blocks:
        if b['t'] == 'h2':
            sid = slug(b['text'])
            out.append('<h2 id="%s">%s</h2>' % (sid, esc(b['text'])))
        elif b['t'] == 'h3':
            sid = slug(b['text'])
            out.append('<h3 id="%s">%s</h3>' % (sid, esc(b['text'])))
            toc.append({'id': sid, 'text': b['text']})
        elif b['t'] == 'note':
            out.append('<p class="note">%s</p>' % b['html'])
        elif b['t'] == 'img':
            out.append('<img class="photo" src="%s" alt="%s">' % (esc(b['src']), esc(b['alt'])))
        elif b['t'] == 'p':
            out.append('<p%s>%s</p>' % (b.get('cls', ''), b['html']))
        elif b['t'] == 'ol':
            bracket = b['items'][0].get('bracket')
            first = b['items'][0]['num']
            if bracket:
                parts = ['<ol class="papers bracket" style="counter-reset: paper %d">' % (first - 1)]
            else:
                start = ' start="%d"' % first if first != 1 else ''
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
                ol_toc.append({'id': anchor, 'text': re.sub(r'<[^>]+>', '', title_html)})
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
    if not toc:
        toc = ol_toc
    return '\n'.join(out), toc


def toc_html(toc):
    if not toc:
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
        if page_id == 'talks':
            toc = []
        if page_id == 'home':
            m = re.match(r'(<img[^>]*>)\s*(<p>.*?</p>)\s*(.*)', body, re.S)
            gh = ('<p class="home-links"><a href="https://github.com/Aristxcy" aria-label="GitHub">'
                  '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
                  '<path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56 0-.28-.01-1.02-.02-2-3.2.7-3.88-1.54-3.88-1.54-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.03 1.76 2.7 1.25 3.35.96.1-.75.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.05 0 0 .96-.31 3.15 1.18a10.9 10.9 0 0 1 5.74 0c2.18-1.49 3.14-1.18 3.14-1.18.63 1.59.24 2.76.12 3.05.74.81 1.18 1.83 1.18 3.09 0 4.41-2.69 5.38-5.26 5.66.41.36.78 1.05.78 2.13 0 1.54-.01 2.78-.01 3.16 0 .31.21.67.8.56A10.52 10.52 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z"/>'
                  '</svg></a></p>')
            main_html = ('<div class="home-grid">\n<div class="home-left">\n%s\n%s\n%s\n</div>\n'
                         '<div class="home-right">\n%s\n</div>\n</div>\n'
                         '<p class="updated">Last updated: %s</p>'
                         % (m.group(1), m.group(2), gh, m.group(3),
                            datetime.date.today().isoformat()))
        elif toc:
            main_html = '<div class="page-body">\n%s\n</div>\n%s' % (body, toc_html(toc))
        else:
            main_html = body
        nav = '\n'.join('    <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == fname else '', t) for h, t in NAV)
        html = TEMPLATE.format(title=title, desc=desc, nav=nav, main=main_html,
                               mainclass=' content-home' if page_id == 'home' else '')
        io.open(os.path.join(ROOT, fname), 'w', encoding='utf-8').write(html)
        print('built', fname)


if __name__ == '__main__':
    main()
