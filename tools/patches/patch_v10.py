#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v10：修「访问量徽章 与 彩蛋提示条 重叠」
#   宽屏：提示条改为靠右定位（紧邻音乐按钮左侧），不再从屏幕正中往左铺
#   窄屏：提示条上移一行（bottom:62px），与底部两个圆徽章分两行堆叠，彻底避免重叠
import io
import os

P = '/root/websrc/fun_egg.html'
MARK = '/* hint-layout-v10 */'
NEW_FIRST = ('#egg-hint{position:fixed;right:70px;bottom:12px;z-index:61;'
             'max-width:calc(100vw - 250px);')

s = io.open(P, encoding='utf-8').read()

if MARK in s:
    print('--: v10 布局已应用过，跳过')
    raise SystemExit(0)

lines = s.split('\n')
done_first = False
for i, ln in enumerate(lines):
    if ln.startswith('#egg-hint{position:fixed;'):
        lines[i] = NEW_FIRST
        done_first = True
        break

if not done_first:
    raise SystemExit('!! 找不到 #egg-hint 定位行')

MEDIA = ('@media (max-width:560px){ ' + MARK + '\n'
         '  #egg-hint{left:50%;right:auto;bottom:62px;transform:translateX(-50%);'
         'max-width:calc(100vw - 28px);font-size:11px;padding:4px 10px}\n'
         '}')

out = []
inserted = False
for ln in lines:
    out.append(ln)
    if not inserted and ln.startswith('#egg-hint:hover'):
        out.append(MEDIA)
        inserted = True

if not inserted:
    raise SystemExit('!! 找不到 #egg-hint:hover 行，未写入')

s = '\n'.join(out)
io.open(P, 'w', encoding='utf-8').write(s)

print('OK: 提示条宽屏改靠右（right:70px）+ 窄屏上移一行（bottom:62px）')
print('    fun_egg.html 现在 %d 字节' % len(s.encode('utf-8')))