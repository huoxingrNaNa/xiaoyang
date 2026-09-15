#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v5：
#  1) 首页作品区只渲染最新 6 个（播放器仍可切换全部 12 个）
#  2) 首页加「查看全部 N 个作品 →」按钮，跳转 works.html
#  3) 用同一份视频数据生成第二页 works.html（展示全部作品）
import io, json, re, shutil

SRC = "/root/websrc/index.html"
TPL = "/root/work_template.html"
OUT = "/root/websrc/works.html"

shutil.copy(SRC, SRC + ".bak_v5")
s = io.open(SRC, encoding="utf-8").read()
before = len(s)

# ---------- 1) 首页网格只渲染 6 个 ----------
pat = re.compile(r'(\n)([ \t]*)for \(var i = 0; i < videos\.length; i\+\+\) \{')


def _limit(m):
    nl, ind = m.group(1), m.group(2)
    return (nl + ind + 'var preview = Math.min(6, videos.length);' +
            nl + ind + 'for (var i = 0; i < preview; i++) {')


s, n = pat.subn(_limit, s)
if n != 1:
    raise SystemExit('[1] 首页网格循环匹配 %d 次，中止' % n)
print('[1-首页限制6个] ok')

# ---------- 2) 加「查看全部」按钮 ----------
pat2 = re.compile(r'(<div class="video-grid" id="video-grid"></div>\s*)(</section>)')
MORE = ('    <div class="works-more">\n'
        '      <a class="mc-btn green" href="works.html">'
        '查看全部 <span data-stat="videos">12</span> 个作品 →</a>\n'
        '    </div>\n  ')


def _more(m):
    return m.group(1) + '\n' + MORE + m.group(2)


s, n = pat2.subn(_more, s)
if n != 1:
    raise SystemExit('[2] 作品区尾部匹配 %d 次，中止' % n)
print('[2-查看全部按钮] ok')

io.open(SRC, "w", encoding="utf-8").write(s)
print('index.html: %d -> %d 字符' % (before, len(s)))

# ---------- 3) 生成第二页 ----------
m = re.search(r'<script id="video-data" type="application/json">(.*?)</script>', s, re.S)
if not m:
    raise SystemExit('[3] 找不到视频数据')
blob = m.group(1)
vids = json.loads(blob)
print('[3-读到视频数据] %d 条' % len(vids))

tpl = io.open(TPL, encoding="utf-8").read()
out = tpl.replace("__VIDEO_DATA__", blob).replace("__COUNT__", str(len(vids)))
io.open(OUT, "w", encoding="utf-8").write(out)
print('works.html 已生成: %d 字节' % len(out.encode("utf-8")))