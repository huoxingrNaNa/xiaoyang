#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v11：注入「访问统计面板（今日新增 + 页面热度榜 + 最近7天柱状图）」
#      并把统计徽章/面板加入彩蛋的「点击排除名单」（免得不小心触发挖方块音效）
import io
import os
import re

DIR = '/root/websrc'
START = '<!-- FUN-STATS-START -->'
END = '<!-- FUN-STATS-END -->'
PAGES = ['index.html', 'works.html', 'game.html']

# ---------- 1) 彩蛋点击排除名单 ----------
p = os.path.join(DIR, 'fun_egg.html')
s = io.open(p, encoding='utf-8').read()
OLD = "closest('a,button,#egg-hint,#egg-mus,.egg-ach')"
NEW = "closest('a,button,#egg-hint,#egg-mus,#egg-stats,#egg-sp,.egg-ach')"
if OLD in s:
    io.open(p, 'w', encoding='utf-8').write(s.replace(OLD, NEW))
    print('OK: 彩蛋点击排除名单已加上 #egg-stats / #egg-sp')
elif NEW in s:
    print('--: 排除名单已是新版')
else:
    print('!! 找不到排除名单，跳过（不影响主功能）')

# ---------- 2) 注入统计面板模块 ----------
stats = io.open(os.path.join(DIR, 'stats_egg.html'), encoding='utf-8').read().strip()
if not (stats.startswith(START) and stats.endswith(END)):
    raise SystemExit('!! stats_egg.html 缺少 START/END 标记')
pat = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)

for name in PAGES:
    pp = os.path.join(DIR, name)
    if not os.path.exists(pp):
        print('!! %s 不存在' % name)
        continue
    t = io.open(pp, encoding='utf-8').read()
    before = len(t.encode('utf-8'))
    if pat.search(t):
        t = pat.sub(lambda m: stats, t)
        tag = '更新'
    else:
        i = t.rfind('</body>')
        if i < 0:
            print('!! %s 找不到 </body>' % name)
            continue
        t = t[:i] + stats + '\n' + t[i:]
        tag = '注入'
    io.open(pp, 'w', encoding='utf-8').write(t)
    print('OK %-12s %s 统计面板  %d -> %d 字节' % (name, tag, before, len(t.encode('utf-8'))))
print('done')