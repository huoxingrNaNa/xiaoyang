#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v8b：把「彩蛋」+「背景音乐」两个模块注入三个页面，并加「方块工坊」入口（幂等）
import io
import os
import re

DIR = '/root/websrc'


def read(p):
    return io.open(p, encoding='utf-8').read()


def write(p, s):
    io.open(p, 'w', encoding='utf-8').write(s)


egg = read(os.path.join(DIR, 'fun_egg.html')).strip()
mus = read(os.path.join(DIR, 'music_egg.html')).strip()

BLOCKS = [(egg, '<!-- FUN-EGG-START -->', '<!-- FUN-EGG-END -->', '彩蛋'),
          (mus, '<!-- FUN-MUSIC-START -->', '<!-- FUN-MUSIC-END -->', '音乐')]

PAGES = ['index.html', 'works.html', 'game.html']

for name in PAGES:
    p = os.path.join(DIR, name)
    if not os.path.exists(p):
        print('!! %s 不存在，跳过' % name)
        continue
    print(name + ':')
    for block, start, end, label in BLOCKS:
        s = read(p)
        before = len(s.encode('utf-8'))
        if start in s:
            s = re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda m: block, s, flags=re.S)
            tag = '更新'
        else:
            i = s.rfind('</body>')
            if i < 0:
                print('  !! 找不到 </body>')
                continue
            s = s[:i] + block + '\n' + s[i:]
            tag = '注入'
        if not s.rstrip().endswith('</html>'):
            print('  !! 结尾异常，放弃写入')
            continue
        write(p, s)
        print('  %s %s  %d -> %d 字节' % (tag, label, before, len(s.encode('utf-8'))))

# ---- 首页：作品区下面加「方块工坊」入口 ----
p = os.path.join(DIR, 'index.html')
s = read(p)
if 'href="game.html"' in s:
    print('index.html 入口：已存在')
else:
    anchor = '<a class="mc-btn green" href="works.html">'
    i = s.find(anchor)
    if i < 0:
        print('!! 首页找不到入口锚点')
    else:
        j = s.find('</a>', i)
        j = s.find('\n', j)
        btn = ('\n      <!-- GAME-LINK -->\n'
               '      <a class="mc-btn green" href="game.html" style="margin-top:12px">'
               '🎮 玩个小游戏 · 方块工坊 →</a>')
        s = s[:j] + btn + s[j:]
        write(p, s)
        print('OK：index.html 已加入方块工坊入口')

# ---- 作品页：导航加个入口 ----
p = os.path.join(DIR, 'works.html')
s = read(p)
if 'href="game.html"' in s:
    print('works.html 入口：已存在')
else:
    anchor = '<a class="back" href="index.html">← 返回首页</a>'
    i = s.find(anchor)
    if i < 0:
        print('!! 作品页找不到导航锚点')
    else:
        j = i + len(anchor)
        s = s[:j] + '<a class="back" href="game.html" style="margin-left:8px">🎮 方块工坊</a>' + s[j:]
        write(p, s)
        print('OK：works.html 导航已加入方块工坊入口')

print('done')