#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v15：SEO / 健壮性补丁
#   1) 三个页面注入 <noscript> 兜底块：JS 没跑起来时，访客/爬虫也能看到内容与入口
#      （index.html / works.html 里还带一份「纯 HTML 作品清单」，由 refresh.py 自动同步刷新）
#   2) 首页注入 JSON-LD 结构化数据（Person），让搜索引擎知道「这是谁」
# 幂等：有标记就替换标记之间的内容；原子：全部校验通过才落盘
import io
import json
import os
import re

DIR = '/root/websrc'
PAGES = ['index.html', 'works.html', 'game.html']
LIST_PAGES = ['index.html', 'works.html']      # 这两页渲染作品卡片，需要纯 HTML 清单

NS_START = '<!-- NOSCRIPT-START -->'
NS_END = '<!-- NOSCRIPT-END -->'
LS_START = '<!-- NOSCRIPT-LIST-START -->'
LS_END = '<!-- NOSCRIPT-LIST-END -->'
JL_START = '<!-- JSONLD-START -->'
JL_END = '<!-- JSONLD-END -->'

SITE = 'https://huoxingrnana.github.io/xiaoyang/'
BILI = 'https://space.bilibili.com/1452804418'

BOX = ('margin:0;padding:16px 18px;background:#eef6ff;border-bottom:3px solid #5fb8f5;'
       'color:#22303c;font-size:14px;line-height:1.75;'
       'font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif')


def esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render_list(vids):
    items = []
    for v in vids:
        items.append(
            '<li style="margin:3px 0">'
            '<a href="https://www.bilibili.com/video/%s/" style="color:#2c7be5;text-decoration:none">%s</a>'
            '<span style="color:#7a8894;font-size:12px"> · %s 播放 · %s</span></li>'
            % (v.get('bvid', ''), esc(v.get('title')), v.get('play', 0), esc(v.get('dur', ''))))
    return (LS_START + '\n<ul style="margin:0;padding-left:20px">'
            + ''.join(items) + '</ul>\n' + LS_END)


def read_videos():
    """从页面里读现成的作品数据（<script id="video-data">），避免自己再拉一次 B 站接口。"""
    for n in LIST_PAGES:
        p = os.path.join(DIR, n)
        if not os.path.isfile(p):
            continue
        s = io.open(p, encoding='utf-8').read()
        m = re.search(r'<script id="video-data" type="application/json">(.*?)</script>', s, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return []


def build_noscript(list_html):
    out = [
        NS_START,
        '<noscript>',
        '<div style="%s">' % BOX,
        '<b style="font-size:15px">⚠️ 你的浏览器没有启用 JavaScript</b>',
        '<p style="margin:6px 0 10px">本站的作品卡片、方块彩蛋和「方块工坊」都需要 JavaScript 才能运行。'
        '<br>下面是可以直接访问的内容：</p>',
    ]
    if list_html:
        out.append(list_html)
    out += [
        '<p style="margin:12px 0 0">'
        '🔗 <a href="%s" style="color:#2c7be5">B站主页（全部作品）</a>'
        ' ｜ <a href="%sworks.html" style="color:#2c7be5">作品页</a>'
        ' ｜ <a href="%sgame.html" style="color:#2c7be5">方块工坊</a>'
        ' ｜ <a href="%s" style="color:#2c7be5">首页</a></p>' % (BILI, SITE, SITE, SITE),
        '</div>',
        '</noscript>',
        NS_END,
    ]
    return '\n'.join(out)


def build_jsonld(desc):
    data = {
        '@context': 'https://schema.org',
        '@type': 'Person',
        'name': 'xiao小小阳',
        'url': SITE,
        'image': SITE + 'avatar.jpg',
        'description': desc,
        'sameAs': [BILI],
    }
    return (JL_START + '\n<script type="application/ld+json">\n'
            + json.dumps(data, ensure_ascii=False, indent=2) + '\n</script>\n' + JL_END)


def upsert_after_body(s, block):
    pat = re.compile(re.escape(NS_START) + '.*?' + re.escape(NS_END), re.S)
    if pat.search(s):
        return pat.sub(lambda m: block, s, count=1), True
    m = re.search(r'<body[^>]*>', s)
    if not m:
        return s, False
    return s[:m.end()] + '\n' + block + s[m.end():], True


def upsert_before_head_end(s, block):
    pat = re.compile(re.escape(JL_START) + '.*?' + re.escape(JL_END), re.S)
    if pat.search(s):
        return pat.sub(lambda m: block, s, count=1)
    if 'application/ld+json' in s:
        return s
    i = s.rfind('</head>')
    if i < 0:
        return s
    return s[:i] + block + '\n' + s[i:]


def main():
    vids = read_videos()
    print('读到作品 %d 个' % len(vids))
    list_html = render_list(vids) if vids else ''

    files = {}
    for n in PAGES:
        p = os.path.join(DIR, n)
        if not os.path.isfile(p):
            print('%-12s 不存在，跳过' % n)
            continue
        files[n] = io.open(p, encoding='utf-8').read()

    # 描述文案直接复用页面已有的 meta description，不自行编造
    desc = 'xiao小小阳的个人主页'
    idx = files.get('index.html', '')
    for pat in (r'<meta property="og:description" content="([^"]*)"',
                r'<meta name="description" content="([^"]*)"'):
        m = re.search(pat, idx)
        if m:
            desc = m.group(1)
            break
    print('JSON-LD 描述: %s' % desc)

    out = {}
    for n, s in files.items():
        blk = build_noscript(list_html if n in LIST_PAGES else '')
        s2, ok = upsert_after_body(s, blk)
        if not ok:
            raise SystemExit('!! %s 找不到 <body> 锚点' % n)
        if n == 'index.html':
            s2 = upsert_before_head_end(s2, build_jsonld(desc))
        out[n] = s2

    # ---------- 校验（全部通过才落盘）----------
    for n, s2 in out.items():
        if s2.count(NS_START) != 1 or s2.count(NS_END) != 1:
            raise SystemExit('!! %s noscript 标记异常' % n)
        if n in LIST_PAGES and list_html and (s2.count(LS_START) != 1 or s2.count(LS_END) != 1):
            raise SystemExit('!! %s 作品清单标记异常' % n)
        if n == 'index.html' and s2.count('application/ld+json') != 1:
            raise SystemExit('!! index.html JSON-LD 异常')
        if not s2.rstrip().endswith('</html>'):
            raise SystemExit('!! %s 结构损坏' % n)

    for n, s2 in out.items():
        io.open(os.path.join(DIR, n), 'w', encoding='utf-8').write(s2)
        print('%-12s 已更新 -> %d 字节' % (n, len(s2.encode('utf-8'))))
    print('done')


if __name__ == '__main__':
    main()