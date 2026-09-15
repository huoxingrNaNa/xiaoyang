#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v14：
#   1) PWA：把「manifest + 主屏图标 + Service Worker 注册」注入三个页面的 <head>
#   2) 作品热度榜：在 works.html 注入「Top5 播放量榜 + 卡片播放量条」
# 均为幂等（重复运行只更新内容，不会叠加）
import io
import os
import re

DIR = '/root/websrc'
PAGES = ['index.html', 'works.html', 'game.html']


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


pwa = read(os.path.join(DIR, 'pwa_head.html')).strip()
rank = read(os.path.join(DIR, 'works_rank.html')).strip()

if not (pwa.startswith('<!-- PWA-HEAD-START -->') and pwa.endswith('<!-- PWA-HEAD-END -->')):
    raise SystemExit('!! pwa_head.html 缺少标记')
if not (rank.startswith('<!-- WORKS-RANK-START -->') and rank.endswith('<!-- WORKS-RANK-END -->')):
    raise SystemExit('!! works_rank.html 缺少标记')

# ---------- 1) PWA 头部 ----------
pat = re.compile(re.escape('<!-- PWA-HEAD-START -->') + r'.*?' + re.escape('<!-- PWA-HEAD-END -->'), re.S)
for name in PAGES:
    p = os.path.join(DIR, name)
    s = read(p)
    before = len(s.encode('utf-8'))
    if pat.search(s):
        s = pat.sub(lambda m: pwa, s)
        tag = '更新'
    else:
        i = s.find('</head>')
        if i < 0:
            print('!! %s 找不到 </head>' % name)
            continue
        s = s[:i] + pwa + '\n' + s[i:]
        tag = '注入'
    write(p, s)
    print('OK %-12s %s PWA头部  %d -> %d 字节' % (name, tag, before, len(s.encode('utf-8'))))

# ---------- 2) 作品热度榜（只给 works.html） ----------
pat2 = re.compile(re.escape('<!-- WORKS-RANK-START -->') + r'.*?' + re.escape('<!-- WORKS-RANK-END -->'), re.S)
p = os.path.join(DIR, 'works.html')
s = read(p)
before = len(s.encode('utf-8'))
if pat2.search(s):
    s = pat2.sub(lambda m: rank, s)
    tag = '更新'
else:
    i = s.rfind('</body>')
    if i < 0:
        raise SystemExit('!! works.html 找不到 </body>')
    s = s[:i] + rank + '\n' + s[i:]
    tag = '注入'
write(p, s)
print('OK works.html   %s 热度榜  %d -> %d 字节' % (tag, before, len(s.encode('utf-8'))))

print('done')