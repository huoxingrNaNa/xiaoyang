#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v17-README：把「彩蛋手机适配」补进 tools/README.md 的文档里
import io

P = '/root/websrc/tools/README.md'

A_OLD = '│   ├── patch_v16.py           ← 一次性：让 refresh.py 顺带更新 noscript 作品清单'
A_NEW = (A_OLD + '\n'
         '│   ├── patch_v17.py           ← 一次性：彩蛋手机适配（长按手势 + 提示条文案分端）')

B_OLD = ('`patch_site_v3` / `v4` / `v5` / `v6` / `v10` / `v12` / `v13` / `patch_music_hook` '
         '/ `patch_readme_v8` / `patch_v16`')
B_NEW = B_OLD + ' / `patch_v17`'

C_OLD = '- **补丁里的 `DIR` 硬编码为 `/root/websrc`**'
C_NEW = ('- **彩蛋的手机适配（v17）**：触屏设备没有键盘，所以「创造模式」钻石雨改用手势触发 —— '
         '**长按屏幕 1.2 秒**（移动超过 12px 或落在按钮/链接上会取消，不会影响滑动与点击）；'
         '提示条文案按 `html.is-touch` 分端显示（电脑给键位、手机给手势）。\n'
         '- **补丁里的 `DIR` 硬编码为 `/root/websrc`**')

PAIRS = [(A_OLD, A_NEW), (B_OLD, B_NEW), (C_OLD, C_NEW)]

s = io.open(P, encoding='utf-8').read()
if 'patch_v17.py' in s:
    print('tools/README.md 已含 v17 说明，无需改动')
    raise SystemExit(0)

for idx, (old, new) in enumerate(PAIRS, 1):
    c = s.count(old)
    if c != 1:
        raise SystemExit('!! 第 %d 处匹配 %d 次（应为 1 次），未写入' % (idx, c))
    s = s.replace(old, new)

io.open(P, 'w', encoding='utf-8').write(s)
print('tools/README.md 已更新 -> %d 字节' % len(s.encode('utf-8')))
print('done')