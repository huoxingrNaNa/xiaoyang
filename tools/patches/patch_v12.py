#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v12：逐日统计统一按「北京时间 UTC+8」分桶
#      否则不同时区的访客会把同一天的数据拆到不同日期键上，逐日排行榜就乱了
import io

DIR = '/root/websrc'
n = 0

# ---------- 1) 前端模块 ----------
p = DIR + '/stats_egg.html'
s = io.open(p, encoding='utf-8').read()

if 'ymdCN' not in s:
    old = '  var today = ymd(new Date());'
    new = ('  /* 统一按北京时间（UTC+8）分桶：不然海外访客会把同一天拆到不同日期键 */\n'
           '  function ymdCN(ts) {\n'
           '    var t = new Date(ts + 8 * 3600000);\n'
           '    return t.getUTCFullYear() + pad(t.getUTCMonth() + 1) + pad(t.getUTCDate());\n'
           '  }\n'
           '  var today = ymdCN(Date.now());')
    if old in s:
        s = s.replace(old, new)
        n += 1
        print('OK: 前端已改用北京时间分桶')
    else:
        print('!! 前端 today 锚点未找到')

    old2 = ('    var out = [], now = new Date();\n'
            '    for (var i = n - 1; i >= 0; i--) out.push(ymd(new Date(now.getTime() - i * 86400000)));')
    new2 = ('    var out = [], base = Date.now();\n'
            '    for (var i = n - 1; i >= 0; i--) out.push(ymdCN(base - i * 86400000));')
    if old2 in s:
        s = s.replace(old2, new2)
        n += 1
        print('OK: 最近 7 天列表也改用北京时间')
    else:
        print('!! lastDays 锚点未找到')
    io.open(p, 'w', encoding='utf-8').write(s)
else:
    print('--: 前端已是北京时间版本')

# ---------- 2) 统计脚本 ----------
p2 = '/root/site_stats.py'
t = io.open(p2, encoding='utf-8').read()
if 'timezone(' not in t:
    old3 = 'def main():\n    today = datetime.date.today()'
    new3 = ('def main():\n'
            '    tz = datetime.timezone(datetime.timedelta(hours=8))  # 北京时间\n'
            '    now = datetime.datetime.now(tz)\n'
            '    today = now.date()')
    if old3 in t:
        t = t.replace(old3, new3)
        t = t.replace("today.strftime('%Y-%m-%d %H:%M')", "now.strftime('%Y-%m-%d %H:%M')")
        io.open(p2, 'w', encoding='utf-8').write(t)
        n += 1
        print('OK: 脚本已改用北京时间（含打印时间修正）')
    else:
        print('!! 脚本 main 锚点未找到')
else:
    print('--: 脚本已是北京时间版本')

print('共改动 %d 处' % n)