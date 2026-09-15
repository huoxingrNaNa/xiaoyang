#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v9：注入「访问量徽章」模块；顺手把彩蛋提示条在窄屏收窄，给徽章让位（幂等）
import io
import os
import re

DIR = '/root/websrc'
START = '<!-- FUN-STATS-START -->'
END = '<!-- FUN-STATS-END -->'
PAGES = ['index.html', 'works.html', 'game.html']

# ---------- 1) 提示条收窄（避免和左下角徽章在手机上打架） ----------
egg_path = os.path.join(DIR, 'fun_egg.html')
s = io.open(egg_path, encoding='utf-8').read()
OLD = 'z-index:61;max-width:92vw;'
NEW = 'z-index:61;max-width:calc(100vw - 210px);'
if OLD in s:
    s = s.replace(OLD, NEW)
    io.open(egg_path, 'w', encoding='utf-8').write(s)
    print('OK: 彩蛋提示条已在窄屏收窄（给访问徽章让位）')
elif NEW in s:
    print('--: 提示条已是收窄版')
else:
    print('!! 未找到提示条 max-width，跳过')

# ---------- 2) 注入统计模块 ----------
stats = io.open(os.path.join(DIR, 'stats_egg.html'), encoding='utf-8').read().strip()
if not (stats.startswith(START) and stats.endswith(END)):
    raise SystemExit('!! stats_egg.html 缺少 START/END 标记')
pat = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)

for name in PAGES:
    p = os.path.join(DIR, name)
    if not os.path.exists(p):
        print('!! %s 不存在' % name)
        continue
    s = io.open(p, encoding='utf-8').read()
    before = len(s.encode('utf-8'))
    if pat.search(s):
        s = pat.sub(lambda m: stats, s)
        tag = '更新'
    else:
        i = s.rfind('</body>')
        if i < 0:
            print('!! %s 找不到 </body>' % name)
            continue
        s = s[:i] + stats + '\n' + s[i:]
        tag = '注入'
    io.open(p, 'w', encoding='utf-8').write(s)
    print('OK %-12s %s 统计徽章  %d -> %d 字节' % (name, tag, before, len(s.encode('utf-8'))))
print('done')