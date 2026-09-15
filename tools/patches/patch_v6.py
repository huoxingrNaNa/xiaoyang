#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v6：暗色模式背景改回「蓝天渐变」的同一套结构（0% / 40% / 100% 三段），只整体压暗
#     浅色模式保持不变；粒子颜色在暗色下提亮一点，便于在蓝底上看清
import io, shutil

OLD_LIGHT_BG = "linear-gradient(180deg, #5fb8f5 0%, #8ed0fb 40%, #c6e9ff 100%)"
OLD_DARK_BG = "linear-gradient(180deg, #070b14 0%, #10192e 45%, #1b2740 100%)"
NEW_DARK_BG = "linear-gradient(180deg, #123b60 0%, #2a5d8b 40%, #4d84b5 100%)"

FILES = ["/root/websrc/index.html", "/root/websrc/works.html"]

for path in FILES:
    shutil.copy(path, path + ".bak_v6")
    s = io.open(path, encoding="utf-8").read()
    before = len(s)

    n = s.count(OLD_DARK_BG)
    if n != 1:
        raise SystemExit("[%s] 暗色背景匹配 %d 次，中止" % (path, n))
    s = s.replace(OLD_DARK_BG, NEW_DARK_BG)

    # 浅色背景必须原样保留（自检）
    if OLD_LIGHT_BG not in s:
        raise SystemExit("[%s] 浅色背景丢失，中止" % path)

    # 首页：暗色下粒子提亮
    if path.endswith("index.html"):
        if '(DARK ? "#39d353" : "#7cbd4b")' in s:
            s = s.replace('(DARK ? "#39d353" : "#7cbd4b")', '(DARK ? "#8ef07a" : "#7cbd4b")')
        if '(DARK ? "#cfe6ff" : "#ffffff")' in s:
            s = s.replace('(DARK ? "#cfe6ff" : "#ffffff")', '(DARK ? "#eaf6ff" : "#ffffff")')

    io.open(path, "w", encoding="utf-8").write(s)
    print("%-34s %d -> %d 字符" % (path.split("/")[-1], before, len(s)))

print("OK：暗色背景 -> %s" % NEW_DARK_BG)