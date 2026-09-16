#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v18-README：把「日期相对化 / 提示条分端判定修正」补进 tools/README.md
import io

P = '/root/websrc/tools/README.md'

A_OLD = '│   ├── patch_v17.py           ← 一次性：彩蛋手机适配（长按手势 + 提示条文案分端）'
A_NEW = (A_OLD + '\n'
         '│   ├── patch_v18.py           ← 一次性：提示条改按「主输入设备」判定 + 更新日期相对化')

B_OLD = '`patch_readme_v8` / `patch_v16` / `patch_v17`'
B_NEW = B_OLD + ' / `patch_v18`'

C_OLD = '- **补丁里的 `DIR` 硬编码为 `/root/websrc`**'
C_NEW = (
    '- **日期口径（v18）**：`refresh.py` 统一按**北京时间 UTC+8** 取年月日（`ymd_cn()`），与站点统计口径一致；'
    '同时写入 `<span data-at="2026-09-17T00:19:33+08:00">` 机器可读时间戳，页面用 JS 显示成「X 小时前」。'
    '这样即使 GitHub 定时任务排队延后（本仓库实测晚 5 小时左右），页面看着也不会「过期」。\n'
    '- **提示条分端判定（v18）**：必须用 CSS 媒体查询 `(hover: none), (pointer: coarse)` 判断主输入设备；'
    '**不要**用 JS 的 `ontouchstart` / `maxTouchPoints` —— 触屏笔记本（有鼠标也有触摸屏）会被误判成手机，'
    '导致电脑上显示「长按屏幕」而不是箭头秘籍。\n'
    '- **GitHub 定时任务不准点**：`update.yml` 里写的 cron 只是「排队时间」，实测本仓库延迟 5 小时以上，'
    '所以任何依赖「定时任务运行时刻」的显示逻辑都不可靠，要用相对时间。\n'
    '- **补丁里的 `DIR` 硬编码为 `/root/websrc`**')

PAIRS = [(A_OLD, A_NEW), (B_OLD, B_NEW), (C_OLD, C_NEW)]

s = io.open(P, encoding='utf-8').read()
if 'patch_v18.py' in s:
    print('tools/README.md 已含 v18 说明，无需改动')
    raise SystemExit(0)

for idx, (old, new) in enumerate(PAIRS, 1):
    c = s.count(old)
    if c != 1:
        raise SystemExit('!! 第 %d 处匹配 %d 次（应为 1 次），未写入' % (idx, c))
    s = s.replace(old, new)

io.open(P, 'w', encoding='utf-8').write(s)
print('tools/README.md 已更新 -> %d 字节' % len(s.encode('utf-8')))
print('done')