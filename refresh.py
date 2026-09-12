#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""刷新 xiaoyang 主页的数据：视频卡片 + 粉丝/视频/获赞 + 更新日期。

用法:
    python3 refresh.py                # 拉数据 -> 改 index.html -> 上传 GitHub
    python3 refresh.py --local-only   # 只改本地文件，不上传（给 GitHub Actions 用）

数据来源（B 站 App 签名接口，不需要登录 / Cookie）：
    app.bilibili.com/x/v2/space/archive/cursor   -> 投稿列表（含播放量、封面、时长）
    api.bilibili.com/x/web-interface/card        -> 粉丝数 / 获赞数
"""
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

APPKEY = '1d8b6e7d45233436'
APPSEC = '560c52ccd288fed045859ed18bffd973'
MID = '1452804418'

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'index.html')
UA = 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36'


def http_json(url, params=None):
    if params:
        params = dict(params)
        params['appkey'] = APPKEY
        params['ts'] = str(int(time.time()))
        qs = urllib.parse.urlencode(sorted(params.items()))
        sign = hashlib.md5((qs + APPSEC).encode('utf-8')).hexdigest()
        url = url + '?' + qs + '&sign=' + sign
    req = urllib.request.Request(url)
    req.add_header('User-Agent', UA)
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode('utf-8'))


def fetch_videos():
    d = http_json('https://app.bilibili.com/x/v2/space/archive/cursor', {
        'mobi_app': 'android', 'platform': 'android',
        'order': 'pubdate', 'pn': 1, 'ps': 30, 'vmid': MID,
    })
    if d.get('code') != 0:
        raise RuntimeError('投稿接口返回 code=%s %s' % (d.get('code'), d.get('message')))
    items = (d.get('data') or {}).get('item') or []
    vids = []
    for v in items:
        dur = v.get('duration') or 0
        vids.append({
            'bvid': v['bvid'],
            'title': v['title'],
            'cover': v['cover'].replace('http://', 'https://') + '@480w_300h_1c.webp',
            'play': v.get('play') or 0,
            'dur': '%d:%02d' % (dur // 60, dur % 60),
            'date': time.strftime('%Y-%m-%d', time.localtime(v['ctime'])) if v.get('ctime') else '',
        })
    return (d.get('data') or {}).get('count') or len(vids), vids


def fetch_stats(old_likes):
    d = http_json('https://api.bilibili.com/x/web-interface/card?mid=%s&photo=false' % MID)
    card = ((d.get('data') or {}).get('card') or {})
    likes = card.get('likes')
    if likes in (None, 0):
        likes = old_likes
    return {'fans': card.get('fans'), 'likes': likes}


def set_stat(html, key, value):
    new, n = re.subn(r'data-stat="%s">[^<]*<' % key, 'data-stat="%s">%s<' % (key, value), html)
    return new, n


def patch_html(html, total, vids, stats):
    blob = json.dumps(vids, ensure_ascii=False, separators=(',', ':'))
    pat = re.compile(r'(<!-- VIDEOS-DATA-START.*?-->)(\s*<script id="video-data" type="application/json">).*?(</script>)', re.S)
    html, n = pat.subn(lambda m: m.group(1) + m.group(2) + blob + m.group(3), html)
    if n != 1:
        raise RuntimeError('视频数据区匹配 %d 次，中止' % n)

    html, _ = set_stat(html, 'videos', total)
    html, _ = set_stat(html, 'updated', time.strftime('%Y-%m-%d'))
    if stats.get('fans') is not None:
        html, _ = set_stat(html, 'fans', stats['fans'])
    if stats.get('likes') is not None:
        html, _ = set_stat(html, 'likes', stats['likes'])
    return html


def current_likes(html):
    m = re.search(r'data-stat="likes">(\d+)<', html)
    return int(m.group(1)) if m else None


def main():
    local_only = '--local-only' in sys.argv
    html = io.open(SRC, encoding='utf-8').read()

    try:
        total, vids = fetch_videos()
        stats = fetch_stats(current_likes(html))
    except Exception as e:
        print('拉取 B 站数据失败：%s' % e)
        print('（网络不通或被风控时不影响线上页面，本次不做任何修改）')
        return 0

    new = patch_html(html, total, vids, stats)
    print('视频 %d 个 / 粉丝 %s / 获赞 %s' % (total, stats.get('fans'), stats.get('likes')))
    if new == html:
        print('页面数据无变化')
    else:
        io.open(SRC, 'w', encoding='utf-8').write(new)
        print('index.html 已更新（%d -> %d 字符）' % (len(html), len(new)))

    if local_only:
        return 0

    sys.path.insert(0, HERE)
    import upload as up
    full = up.resolve_repo()
    up.put(full, 'index.html', 'chore: 自动更新作品数据')
    print('线上地址: https://%s.github.io/%s/' % (up.OWNER.lower(), up.REPO))
    return 0


if __name__ == '__main__':
    sys.exit(main())