#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v7：给 index.html / works.html 注入「方块世界彩蛋」块（幂等）
#   - 成就弹窗（初次见面 / 旅行者 / 鉴赏家 / 挖掘 15 下 / F3 / 创造模式）
#   - 点击任意处：挖掘音效 + 草方块粒子
#   - Konami 秘籍：钻石雨 + /gamemode creative
#   - F3 调试屏（桌面按 F3 / 手机点提示条）
import io
import re
import os

DIR = '/root/websrc'
EGG_SRC = os.path.join(DIR, 'fun_egg.html')
START = '<!-- FUN-EGG-START -->'
END = '<!-- FUN-EGG-END -->'
FILES = ['index.html', 'works.html']

egg = io.open(EGG_SRC, encoding='utf-8').read().strip()
if not (egg.startswith(START) and egg.endswith(END)):
    raise SystemExit('!! fun_egg.html 缺少 START/END 标记')
print('彩蛋块: %d 字节' % len(egg.encode('utf-8')))

pat = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)

for name in FILES:
    path = os.path.join(DIR, name)
    s = io.open(path, encoding='utf-8').read()
    before = len(s)
    if pat.search(s):
        s = pat.sub(lambda m: egg, s)
        how = '替换旧彩蛋块'
    else:
        i = s.rfind('</body>')
        if i < 0:
            print('!! %s 里找不到 </body>，跳过' % name)
            continue
        s = s[:i] + egg + '\n' + s[i:]
        how = '新增'
    if not s.rstrip().endswith('</html>'):
        print('!! %s 结尾异常，未写入' % name)
        continue
    io.open(path, 'w', encoding='utf-8').write(s)
    print('OK %-12s %s  %d -> %d 字节' % (name, how, before, len(s)))

print('done')
