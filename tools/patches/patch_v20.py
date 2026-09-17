#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v20：状态徽章 + 状态后门
#   1) index.html：把 presence.html 模块注入 hero（名字下面）
#   2) sw.js：VER 升到 v2；presence.txt 走「网络优先」，绝不长期缓存
#   3) tools/rebuild.sh：把 v20 加进重建链，并校验状态徽章标记
#   4) tools/README.md：补文档（后门怎么用、三源降级、钥匙在哪）
# 全部替换点先校验 count==1，再原子落盘
import io
import os
import re

DIR = '/root/websrc'
IDX = os.path.join(DIR, 'index.html')
SW = os.path.join(DIR, 'sw.js')
RBS = os.path.join(DIR, 'tools', 'rebuild.sh')
RDM = os.path.join(DIR, 'tools', 'README.md')

report = []

# ============ 1) index.html 注入状态徽章 ============
mod = io.open(os.path.join(DIR, 'presence.html'), encoding='utf-8').read().rstrip() + '\n'
s = io.open(IDX, encoding='utf-8').read()

pat = re.compile(re.escape('<!-- PRESENCE-BADGE-START -->') + '.*?' + re.escape('<!-- PRESENCE-BADGE-END -->'), re.S)
if pat.search(s):
    s2 = pat.sub(lambda m: mod.rstrip(), s, count=1)
    if s2 != s:
        io.open(IDX, 'w', encoding='utf-8').write(s2)
        report.append('index.html 状态徽章已刷新 -> %d 字节' % len(s2.encode('utf-8')))
    else:
        report.append('index.html 状态徽章已是最新，跳过')
else:
    ANCHOR = '<h1 class="hero-name">xiao小小阳</h1>'
    if s.count(ANCHOR) != 1:
        raise SystemExit('!! index.html 找不到唯一的 hero 名字行（%d 处）' % s.count(ANCHOR))
    s2 = s.replace(ANCHOR, ANCHOR + '\n\n' + mod.rstrip())
    if s2.count('PRESENCE-BADGE-START') != 1 or not s2.rstrip().endswith('</html>'):
        raise SystemExit('!! index.html 注入自检失败')
    io.open(IDX + '.bak_v20', 'w', encoding='utf-8').write(s)
    io.open(IDX, 'w', encoding='utf-8').write(s2)
    report.append('index.html 已注入状态徽章 -> %d 字节' % len(s2.encode('utf-8')))

# ============ 2) sw.js：版本 + presence.txt 网络优先 ============
s = io.open(SW, encoding='utf-8').read()
if 'presence.txt' in s:
    report.append('sw.js 已处理过，跳过')
else:
    A_OLD = "var VER = 'v1';"
    A_NEW = "var VER = 'v2';"
    B_OLD = ("  e.respondWith(\n"
             "    caches.match(req).then(function (hit) {")
    B_NEW = ("  /* presence.txt：网络优先，尽量别吃缓存 —— 否则后门改了状态要等缓存过期才看到 */\n"
             "  if (/\\/presence\\.txt$/i.test(url.pathname)) {\n"
             "    e.respondWith(\n"
             "      fetch(req).then(function (r) {\n"
             "        var cp = r.clone();\n"
             "        caches.open(CACHE).then(function (c) { c.put(req, cp); });\n"
             "        return r;\n"
             "      }).catch(function () { return caches.match(req); })\n"
             "    );\n"
             "    return;\n"
             "  }\n\n"
             "  e.respondWith(\n"
             "    caches.match(req).then(function (hit) {")
    for idx, (old, new) in enumerate([(A_OLD, A_NEW), (B_OLD, B_NEW)], 1):
        if s.count(old) != 1:
            raise SystemExit('!! sw.js 第 %d 处匹配 %d 次（应为 1）' % (idx, s.count(old)))
        s = s.replace(old, new)
    if 'presence.txt' not in s or "'v2'" not in s:
        raise SystemExit('!! sw.js 自检失败')
    io.open(SW + '.bak_v20', 'w', encoding='utf-8').write(io.open(SW, encoding='utf-8').read())
    io.open(SW, 'w', encoding='utf-8').write(s)
    report.append('sw.js 已更新 -> %d 字节' % len(s.encode('utf-8')))

# ============ 3) rebuild.sh：加入 v20 + 校验标记 ============
s = io.open(RBS, encoding='utf-8').read()
if 'patch_v20.py' in s:
    report.append('rebuild.sh 已含 v20，跳过')
else:
    C_OLD = 'run "6/6 noscript + JSON-LD (v15)" tools/patches/patch_v15.py'
    C_NEW = ('run "6/7 noscript + JSON-LD (v15)" tools/patches/patch_v15.py\n'
             'run "7/7 状态徽章 + 后门 (v20)" tools/patches/patch_v20.py')
    D_OLD = "print('结果：', '✓ 全部模块就位' if ok else '✗ 有模块异常，请检查上面的补丁输出')"
    D_NEW = ("si = io.open(os.path.join(d, 'index.html'), encoding='utf-8').read()\n"
             "if si.count('PRESENCE-BADGE-START') != 1:\n"
             "    print('   index.html   状态徽章缺失'); ok = False\n"
             + D_OLD)
    for idx, (old, new) in enumerate([(C_OLD, C_NEW), (D_OLD, D_NEW)], 1):
        if s.count(old) != 1:
            raise SystemExit('!! rebuild.sh 第 %d 处匹配 %d 次（应为 1）' % (idx, s.count(old)))
        s = s.replace(old, new)
    io.open(RBS, 'w', encoding='utf-8').write(s)
    report.append('rebuild.sh 已更新 -> %d 字节' % len(s.encode('utf-8')))

# ============ 4) tools/README.md ============
s = io.open(RDM, encoding='utf-8').read()
if 'presence.html' in s:
    report.append('tools/README.md 已含 v20 说明，跳过')
else:
    E_OLD = '│   └── works_rank.html        ← 作品热度榜：Top5 播放量榜 + 每张卡片的播放量条'
    E_NEW = '│   ├── works_rank.html        ← 作品热度榜：Top5 播放量榜 + 每张卡片的播放量条' + '\n│   └── presence.html          ← 状态徽章 + 状态后门面板（三源降级）'
    F_OLD = '│   ├── patch_v18.py           ← 一次性：提示条改按「主输入设备」判定 + 更新日期相对化'
    F_NEW = F_OLD + '\n│   ├── patch_v20.py           ← 注入状态徽章 + 后门（并让 sw.js 不缓存 presence.txt）'
    G_OLD = '`patch_readme_v8` / `patch_v16` / `patch_v17` / `patch_v18`'
    G_NEW = G_OLD + ' / `patch_v20`'
    H_OLD = '## 日常操作'
    H_NEW = '''## 🔐 状态后门怎么用（v20）

**入口**：首页 hero 里的状态徽章 → **2 秒内连点 5 下** 打开设置面板；也可在网址后加 `#admin`。

**能改什么**：在线 / 做动画中 / 忙碌 / 睡觉中 / 离线，外加一句附言（≤40 字），或「恢复自动」。

**数据存在哪（三源降级）**：

| 优先级 | 源 | 说明 |
|---|---|---|
| 1️⃣ | `ntfy.sh/<TOPIC>` | 后门写入的通道，秒级生效。**TOPIC 就是钥匙**，写在 `templates/presence.html` 里，改了等于换钥匙 |
| 2️⃣ | `presence.txt` | 仓库根目录的备用文件。后门面板提示「网络不通」时，用手机 GitHub 改这个文件（一行 `状态\\|附言`，`#` 开头是注释） |
| 3️⃣ | 按北京时间自动 | 07:30–22:30 = 在线，其余 = 睡觉中（时段写在 `presence.html` 的 `SCHED`）。永远有兜底 |

**诚实的限制**：静态站**做不到真正的「在线/离线检测」**（没有服务器盯着你）。
线上真正存在的只有「手动状态」+「按时段猜」，所以这个设计＝手动为主、自动兜底。
另外后门只是「隐蔽入口」，不是安全边界：**能读页面源码的人就能找到通道名**，
最坏情况是有人乱改你的状态显示（改回去就行）。真需要严格权限就得上带后端的方案。

## 日常操作'''

    for idx, (old, new) in enumerate([(E_OLD, E_NEW), (F_OLD, F_NEW), (G_OLD, G_NEW), (H_OLD, H_NEW)], 1):
        if s.count(old) != 1:
            raise SystemExit('!! README 第 %d 处匹配 %d 次（应为 1）' % (idx, s.count(old)))
        s = s.replace(old, new)
    io.open(RDM, 'w', encoding='utf-8').write(s)
    report.append('tools/README.md 已更新 -> %d 字节' % len(s.encode('utf-8')))

print('\n'.join(report))
print('done')