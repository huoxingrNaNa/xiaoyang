#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v16：让 refresh.py 在刷新作品数据时，顺带更新 noscript 里的「纯 HTML 作品清单」
#      否则那份清单会随着 B 站投稿增加而变旧。
#      两个替换点：① 在 patch_html 前插入 render_noscript_list()
#                  ② 在写 data-stat="videos" 前插入清单同步逻辑
# 顺序校验 + 原子落盘
import io
import os

P = '/root/websrc/refresh.py'

A_OLD = 'def patch_html(html, total, vids, stats):'

A_NEW = r'''def render_noscript_list(vids):
    """纯 HTML 作品清单（noscript 兜底用），与 VIDEOS-DATA 同步刷新。"""
    if not vids:
        return None
    items = []
    for v in vids:
        t = (v.get('title') or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        items.append(
            '<li style="margin:3px 0">'
            '<a href="https://www.bilibili.com/video/%s/" style="color:#2c7be5;text-decoration:none">%s</a>'
            '<span style="color:#7a8894;font-size:12px"> · %s 播放 · %s</span></li>'
            % (v.get('bvid', ''), t, v.get('play', 0), v.get('dur', '')))
    return '<ul style="margin:0;padding-left:20px">' + ''.join(items) + '</ul>'


def patch_html(html, total, vids, stats):'''

B_OLD = "    html = set_stat(html, 'videos', total)"

B_NEW = r'''    ns = render_noscript_list(vids)
    pat_ns = re.compile(r'(<!-- NOSCRIPT-LIST-START -->).*?(<!-- NOSCRIPT-LIST-END -->)', re.S)
    if ns and pat_ns.search(html):
        html = pat_ns.sub(lambda m: m.group(1) + '\n' + ns + '\n' + m.group(2), html, count=1)

    html = set_stat(html, 'videos', total)'''

PAIRS = [(A_OLD, A_NEW), (B_OLD, B_NEW)]

s = io.open(P, encoding='utf-8').read()

if 'render_noscript_list' in s:
    print('refresh.py 已是 v16 版本，无需改动')
    raise SystemExit(0)

out = s
for idx, (old, new) in enumerate(PAIRS, 1):
    if out.count(old) != 1:
        raise SystemExit('!! 第 %d 个锚点匹配 %d 次（应为 1 次），未写入' % (idx, out.count(old)))
    out = out.replace(old, new)

if 'render_noscript_list' not in out or 'NOSCRIPT-LIST-START' not in out:
    raise SystemExit('!! 自检失败，未写入')

io.open(P + '.bak_v16', 'w', encoding='utf-8').write(s)
io.open(P, 'w', encoding='utf-8').write(out)
print('refresh.py 已升级 -> %d 字节（备份 refresh.py.bak_v16）' % len(out.encode('utf-8')))
print('done')