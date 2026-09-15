#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xiaoyang 站点统计（一条命令看全部）
用法：
    python3 /root/site_stats.py          # 逐日榜查最近 30 天
    python3 /root/site_stats.py 90       # 逐日榜查最近 90 天
包含：累计浏览 / 独立访客 / 今日新增 / 今日访客 / 页面热度榜 / 逐日浏览排行 / 仓库流量
"""
import os
import datetime
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = 'huoxingrNaNa/xiaoyang'
BASE = 'https://abacus.jasoncameron.dev/'
NS = 'xiaoyang-site/'


def api(key, timeout=15):
    """读计数器；键不存在/网络失败都返回 None"""
    try:
        req = urllib.request.Request(BASE + 'get/' + key, headers={'User-Agent': 'operit'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            j = json.loads(r.read().decode('utf-8'))
        return j.get('value') if isinstance(j, dict) else None
    except Exception:
        return None


def gh(url):
    req = urllib.request.Request(url, headers={'Authorization': 'token ' + TOKEN, 'User-Agent': 'operit'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def bar(v, mx, width=20):
    return '█' * max(1, int(v / mx * width)) if v else ''


def main():
    tz = datetime.timezone(datetime.timedelta(hours=8))  # 北京时间
    now = datetime.datetime.now(tz)
    today = now.date()
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 30

    print('=' * 60)
    print('xiaoyang 站点统计 · ' + now.strftime('%Y-%m-%d %H:%M'))
    print('=' * 60)

    pv = api(NS + 'hits')
    uv = api(NS + 'visitors')
    dy = api(NS + 'd-' + today.strftime('%Y%m%d'))
    du = api(NS + 'u-' + today.strftime('%Y%m%d'))
    print('  累计浏览 (PV) : %s' % (pv if pv is not None else '—'))
    print('  今日新增 (PV) : %s' % (dy if dy is not None else '—'))
    print('  独立访客 (UV) : %s' % (uv if uv is not None else '—'))
    print('  今日访客 (UV) : %s' % (du if du is not None else '—'))

    print()
    print('  页面热度榜：')
    pages = [('首页', 'p-index'), ('作品页', 'p-works'), ('方块工坊', 'p-game')]
    pvals = [(n, api(NS + k)) for n, k in pages]
    pmax = max([v or 0 for _, v in pvals] + [1])
    for n, v in sorted(pvals, key=lambda x: -(x[1] or 0)):
        print('    %-8s %6s  %s' % (n, v if v is not None else '—', bar(v or 0, pmax)))

    print()
    print('  逐日浏览排行（最近 %d 天，只列有数据的）：' % days)
    dates = [today - datetime.timedelta(days=i) for i in range(days)]
    keys = [(d, NS + 'd-' + d.strftime('%Y%m%d')) for d in dates]
    rows = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for (d, _), v in zip(keys, ex.map(lambda kv: api(kv[1]), keys)):
            if v:
                rows.append((d, v))
    if rows:
        rows.sort(key=lambda x: -x[1])
        mx = rows[0][1]
        week = '一二三四五六日'
        for i, (d, v) in enumerate(rows, 1):
            print('    %2d. %s（周%s） %6d  %s' % (i, d.strftime('%Y-%m-%d'), week[d.weekday()], v, bar(v, mx)))
        print('    ── 这 %d 天合计：%d 次' % (len(rows), sum(v for _, v in rows)))
    else:
        print('    （暂无逐日数据 —— 计数器刚上线时是这样的）')

    print()
    print('  GitHub 仓库（只算仓库页面，和网站访问无关）：')
    try:
        info = gh('https://api.github.com/repos/' + REPO)
        print('    ⭐ %s · 🍴 %s · 👁 %s' % (info.get('stargazers_count'), info.get('forks_count'),
                                             info.get('subscribers_count')))
        v = gh('https://api.github.com/repos/%s/traffic/views' % REPO)
        c = gh('https://api.github.com/repos/%s/traffic/clones' % REPO)
        print('    近14天仓库浏览 %s 次 / %s 独立 · clone %s 次 / %s 独立'
              % (v.get('count'), v.get('uniques'), c.get('count'), c.get('uniques')))
    except Exception as e:
        print('    查询失败：%s' % e)


if __name__ == '__main__':
    main()