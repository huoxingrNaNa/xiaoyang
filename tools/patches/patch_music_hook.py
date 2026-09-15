#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v8a：给彩蛋块加「对外接口」（成就 / 音效 / AudioContext），
#      并让右下角音乐按钮不被当成「挖方块」目标。
import io

P = '/root/websrc/fun_egg.html'
s = io.open(P, encoding='utf-8').read()
n = 0

HOOK = ("  window.xyAch = ach;\n"
        "  window.xySfx = { dig: sfxDig, get: sfxGet, gem: sfxGem, "
        "pop: function () { tone(1046, 0, 0.12, 0.1, 'square'); } };\n"
        "  window.xyAC = ac;\n")

if 'window.xyAch' not in s:
    anchor = '  try {\n    console.log('
    i = s.find(anchor)
    if i < 0:
        raise SystemExit('!! 找不到 hook 插入点')
    s = s[:i] + HOOK + s[i:]
    n += 1
    print('OK: 已插入 window.xyAch / xySfx / xyAC')
else:
    print('--: hook 已存在')

OLD = "closest('a,button,#egg-hint,.egg-ach')"
NEW = "closest('a,button,#egg-hint,#egg-mus,.egg-ach')"
if OLD in s:
    s = s.replace(OLD, NEW)
    n += 1
    print('OK: 挖方块目标已排除 #egg-mus')
else:
    print('--: 选择器已是新版' if NEW in s else '!! 找不到选择器')

io.open(P, 'w', encoding='utf-8').write(s)
print('完成：改动 %d 处，fun_egg.html 现在 %d 字节' % (n, len(s.encode('utf-8'))))