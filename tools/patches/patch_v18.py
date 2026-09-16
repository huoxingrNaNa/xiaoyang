#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v18：
#   1) 修彩蛋提示条：改用「主输入设备」判定（媒体查询 hover/pointer），
#      之前用 JS 的 ontouchstart/maxTouchPoints —— 触屏笔记本（有鼠标也有触摸屏）
#      会被误判成手机，于是电脑上显示「长按屏幕」而不是箭头秘籍。
#   2) 更新日期相对化：hero 显示「数据更新于 X 小时前」，不再依赖定时任务的运行时刻。
#   3) refresh.py：日期统一按北京时间（UTC+8），并额外写入机器可读时间戳 data-at。
# 所有替换点先校验 count==1，再原子落盘
import io
import re

EGG = '/root/websrc/fun_egg.html'
IDX = '/root/websrc/index.html'
RFS = '/root/websrc/refresh.py'

report = []

# ============ 1) 彩蛋提示条：CSS 分端判定 ============
CSS_OLD = """  /* ---- v17：提示条分端文案 ---- */
  #egg-hint .hint-mob{display:none}
  html.is-touch #egg-hint .hint-pc{display:none}
  html.is-touch #egg-hint .hint-mob{display:inline}"""

CSS_NEW = """  /* ---- v18：按主输入设备决定文案（鼠标=键盘秘籍 / 触屏=长按手势）---- */
  #egg-hint .hint-mob{display:none}
  @media (hover: none), (pointer: coarse){
    #egg-hint .hint-pc{display:none}
    #egg-hint .hint-mob{display:inline}
  }"""

JS_OLD = """  function isTouchDevice() { return ('ontouchstart' in window) || (navigator.maxTouchPoints > 0); }
  if (isTouchDevice()) { document.documentElement.className += ' is-touch'; }
"""
JS_NEW = """  /* v18：提示文案改由 CSS 媒体查询（hover/pointer）判定，不再用 JS 猜设备 */
"""

s = io.open(EGG, encoding='utf-8').read()
if 'pointer: coarse' in s:
    report.append('fun_egg.html 已是 v18，跳过')
else:
    for name, old, new in [('CSS', CSS_OLD, CSS_NEW), ('JS', JS_OLD, JS_NEW)]:
        if s.count(old) != 1:
            raise SystemExit('!! fun_egg.html %s 块匹配 %d 次（应为 1）' % (name, s.count(old)))
        s = s.replace(old, new)
    if 'is-touch' in s or 'pointer: coarse' not in s:
        raise SystemExit('!! fun_egg.html 自检失败')
    io.open(EGG + '.bak_v18', 'w', encoding='utf-8').write(
        io.open(EGG, encoding='utf-8').read())
    io.open(EGG, 'w', encoding='utf-8').write(s)
    report.append('fun_egg.html 已更新 -> %d 字节' % len(s.encode('utf-8')))

# ============ 2) index.html：data-at 属性 + 相对时间脚本 ============
s = io.open(IDX, encoding='utf-8').read()

if 'data-at=""' in s:
    report.append('index.html 已含 data-at，跳过')
else:
    AT_OLD = '<p class="hero-updated">数据更新于 <span data-stat="updated">'
    AT_NEW = '<p class="hero-updated">数据更新于 <span data-at="" data-stat="updated">'
    if s.count(AT_OLD) != 1:
        raise SystemExit('!! index.html 更新日期行匹配 %d 次（应为 1）' % s.count(AT_OLD))
    s = s.replace(AT_OLD, AT_NEW)

    m = re.search(r'\n[ \t]*<p class="hero-updated">.*?</p>', s, re.S)
    if not m:
        raise SystemExit('!! index.html 找不到 hero-updated 段落')

    SCRIPT = """
    <script>
    /* v18：把「数据更新于 2026-09-17」换成「数据更新于 9 小时前」（JS 关了就看日期，不影响） */
    (function () {
      var el = document.querySelector('[data-stat="updated"][data-at]');
      if (!el) return;
      var at = el.getAttribute('data-at');
      if (!at) return;
      var t = Date.parse(at);
      if (isNaN(t)) return;
      function upd() {
        var m = Math.floor((Date.now() - t) / 60000), txt;
        if (m < 1) txt = '刚刚';
        else if (m < 60) txt = m + ' 分钟前';
        else if (m < 1440) txt = Math.floor(m / 60) + ' 小时前';
        else txt = Math.floor(m / 1440) + ' 天前';
        if (el.textContent !== txt) el.textContent = txt;
      }
      upd();
      setInterval(upd, 60000);
    })();
    </script>"""
    s = s[:m.end()] + SCRIPT + s[m.end():]

    if s.count('data-at=""') != 1 or 'data-stat="updated"' not in s:
        raise SystemExit('!! index.html 自检失败')
    io.open(IDX + '.bak_v18', 'w', encoding='utf-8').write(
        io.open(IDX, encoding='utf-8').read())
    io.open(IDX, 'w', encoding='utf-8').write(s)
    report.append('index.html 已更新 -> %d 字节' % len(s.encode('utf-8')))

# ============ 3) refresh.py：北京时间 + 写入 data-at ============
s = io.open(RFS, encoding='utf-8').read()

if 'TZ8' in s:
    report.append('refresh.py 已是 v18，跳过')
else:
    H_OLD = 'def set_stat(html, key, value):'
    H_NEW = '''TZ8 = 8 * 3600          # 北京时间 UTC+8（与站点统计口径一致）


def ymd_cn(ts=None):
    """按北京时间取年月日；不传 ts 就取当前时间。"""
    return time.strftime('%Y-%m-%d', time.gmtime((time.time() if ts is None else ts) + TZ8))


def set_at(html, key, value):
    """写入 data-at 属性（机器可读时间戳，供页面算「X 小时前」）。"""
    pat = r'(<span[^>]*data-at=")[^"]*("[^>]*data-stat="%s")' % key
    return re.subn(pat, lambda m: m.group(1) + value + m.group(2), html)[0]


def set_stat(html, key, value):'''

    D1_OLD = "            'date': time.strftime('%Y-%m-%d', time.localtime(v['ctime'])) if v.get('ctime') else '',"
    D1_NEW = "            'date': ymd_cn(v['ctime']) if v.get('ctime') else '',"

    D2_OLD = "    html = set_stat(html, 'updated', time.strftime('%Y-%m-%d'))"
    D2_NEW = ("    html = set_stat(html, 'updated', ymd_cn())\n"
              "    html = set_at(html, 'updated',\n"
              "                  time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.gmtime(time.time() + TZ8)))")

    for idx, (old, new) in enumerate([(H_OLD, H_NEW), (D1_OLD, D1_NEW), (D2_OLD, D2_NEW)], 1):
        if s.count(old) != 1:
            raise SystemExit('!! refresh.py 第 %d 处匹配 %d 次（应为 1）' % (idx, s.count(old)))
        s = s.replace(old, new)

    if 'TZ8' not in s or 'set_at(html' not in s:
        raise SystemExit('!! refresh.py 自检失败')
    io.open(RFS + '.bak_v18', 'w', encoding='utf-8').write(
        io.open(RFS, encoding='utf-8').read())
    io.open(RFS, 'w', encoding='utf-8').write(s)
    report.append('refresh.py 已更新 -> %d 字节' % len(s.encode('utf-8')))

print('\n'.join(report))
print('done')