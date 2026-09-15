#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把本地网页文件上传到 GitHub Pages 仓库（xiaoyang）。

用法:
    python3 upload.py                # 上传下面 UPLOAD 列表里的全部文件
    python3 upload.py index.html     # 只上传指定文件（可写多个）

特点:
    * 先查仓库真实名字 —— 仓库改过名也能自动跟上（之前硬编码 homepage 会 301 失败）
    * 自动读取远端 sha 做更新，新文件则走新增
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

TOKEN = os.environ.get('GITHUB_TOKEN', '')
OWNER = 'huoxingrNaNa'
REPO = 'xiaoyang'

SRC = os.path.dirname(os.path.abspath(__file__))
UPLOAD = ['index.html', 'avatar.jpg', 'README.md']
API = 'https://api.github.com'


def req(method, url, data=None):
    r = urllib.request.Request(url, method=method)
    r.add_header('Authorization', 'token %s' % TOKEN)
    r.add_header('User-Agent', 'operit-deploy')
    r.add_header('Content-Type', 'application/json')
    body = json.dumps(data).encode('utf-8') if data is not None else None
    try:
        with urllib.request.urlopen(r, body, timeout=90) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8') or '{}'
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {'message': raw}


def resolve_repo():
    """解析仓库真实全名（改名后 GET 会 302，urlopen 会自动跟随）。"""
    st, d = req('GET', '%s/repos/%s/%s' % (API, OWNER, REPO))
    if st != 200:
        raise SystemExit('仓库不可访问: HTTP %s / %s' % (st, d.get('message')))
    full = d['full_name']
    if full != '%s/%s' % (OWNER, REPO):
        print('提示: 仓库已改名为 %s（脚本已自动使用新名字）' % full)
    return full


def put(full, name, msg):
    path = os.path.join(SRC, name)
    if not os.path.isfile(path):
        print('%-14s 跳过（本地不存在）' % name)
        return False
    st, d = req('GET', '%s/repos/%s/contents/%s' % (API, full, name))
    sha = d.get('sha') if st == 200 else None
    raw = open(path, 'rb').read()
    payload = {'message': msg, 'content': base64.b64encode(raw).decode()}
    if sha:
        payload['sha'] = sha
    st, d = req('PUT', '%s/repos/%s/contents/%s' % (API, full, name), payload)
    ok = bool(d.get('content'))
    print('%-14s %7d B  HTTP %s  %s' % (name, len(raw), st, 'OK' if ok else d.get('message', 'FAIL')))
    return ok


def main():
    names = sys.argv[1:] or UPLOAD
    full = resolve_repo()
    print('目标仓库: %s' % full)
    for n in names:
        put(full, n, 'update: %s' % n)
    print('线上地址: https://%s.github.io/%s/' % (OWNER.lower(), REPO))


if __name__ == '__main__':
    main()