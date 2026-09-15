#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v8c：README 补上「方块工坊」入口 + 同步 /sdcard/网页 镜像
import io
import os
import shutil

DIR = '/root/websrc'
MIRROR = '/sdcard/网页'

p = os.path.join(DIR, 'README.md')
s = io.open(p, encoding='utf-8').read()

if 'game.html' not in s:
    i = s.find('全部作品')
    if i < 0:
        print('!! README 里找不到「全部作品」锚点，未改动')
    else:
        j = s.find('\n', i)
        line = '\n方块工坊（小游戏）：<https://huoxingrnana.github.io/xiaoyang/game.html>'
        s = s[:j] + line + s[j:]
        io.open(p, 'w', encoding='utf-8').write(s)
        print('OK：README 已加入方块工坊链接')
else:
    print('--：README 已包含 game.html')

os.makedirs(MIRROR, exist_ok=True)
for f in ['index.html', 'works.html', 'game.html', 'fun_egg.html', 'music_egg.html', 'README.md']:
    src = os.path.join(DIR, f)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(MIRROR, f))
        print('镜像 %s -> %d 字节' % (f, os.path.getsize(src)))
print('done')