#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 拉取 GitHub 仓库统计：星标/关注/Fork/浏览量/克隆量/Referrer/下载量
import os
import json, subprocess

TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO = "huoxingrNaNa/QQCatHelper"


def api(path):
    out = subprocess.check_output([
        "curl", "-sS",
        "-H", "Authorization: token " + TOKEN,
        "-H", "Accept: application/vnd.github+json",
        "-H", "User-Agent: repo-stats",
        "https://api.github.com" + path
    ])
    try:
        return json.loads(out.decode("utf-8"))
    except Exception:
        return {"_raw": out.decode("utf-8")[:300]}


print("=" * 52)
print("1) 仓库基本信息 /repos/%s" % REPO)
r = api("/repos/" + REPO)
if isinstance(r, dict) and "stargazers_count" in r:
    print("  可见性      : %s" % r.get("visibility"))
    print("  ⭐ 星标      : %d" % r["stargazers_count"])
    print("  👁 关注(watch): %d" % r["subscribers_count"])
    print("  🍴 Fork      : %d" % r["forks_count"])
    print("  👥 网络成员  : %d" % r.get("network_count", 0))
    print("  ❗ open issues: %d" % r["open_issues_count"])
    print("  创建时间    : %s" % r["created_at"])
    print("  最后推送    : %s" % r["pushed_at"])
else:
    print("  !! %s" % r)

print("=" * 52)
print("2) 浏览量 /traffic/views（近 14 天）")
v = api("/repos/%s/traffic/views" % REPO)
if isinstance(v, dict) and "count" in v:
    print("  总浏览次数: %d    独立访客: %d" % (v["count"], v["uniques"]))
    for d in v.get("views", [])[-14:]:
        print("    %s  views=%-4d uniques=%d" % (d["timestamp"][:10], d["count"], d["uniques"]))
else:
    print("  !! %s" % v)

print("=" * 52)
print("3) 克隆量 /traffic/clones（近 14 天）")
c = api("/repos/%s/traffic/clones" % REPO)
if isinstance(c, dict) and "count" in c:
    print("  总克隆次数: %d    独立克隆者: %d" % (c["count"], c["uniques"]))
else:
    print("  !! %s" % c)

print("=" * 52)
print("4) 访问来源 /traffic/popular/referrers")
ref = api("/repos/%s/traffic/popular/referrers" % REPO)
if isinstance(ref, list):
    if not ref:
        print("  （暂无数据）")
    for x in ref:
        print("  %-20s views=%d uniques=%d" % (x["referrer"], x["count"], x["uniques"]))
else:
    print("  !! %s" % ref)

print("=" * 52)
print("5) Fork 列表 /forks")
f = api("/repos/%s/forks" % REPO)
if isinstance(f, list):
    if not f:
        print("  （暂无 Fork）")
    for x in f:
        print("  %s  (created %s)" % (x["full_name"], x["created_at"]))
else:
    print("  !! %s" % f)

print("=" * 52)
print("6) 星标用户 /stargazers")
g = api("/repos/%s/stargazers" % REPO)
if isinstance(g, list):
    if not g:
        print("  （暂无星标）")
    for x in g:
        print("  %s" % x["login"])
else:
    print("  !! %s" % g)

print("=" * 52)
print("7) 各版本 APK 下载量 /releases")
rel = api("/repos/%s/releases" % REPO)
if isinstance(rel, list):
    total = 0
    for x in rel:
        for a in x.get("assets", []):
            total += a["download_count"]
            print("  %-8s %-24s 下载 %d 次" % (x["tag_name"], a["name"], a["download_count"]))
    print("  ---- 累计下载: %d 次" % total)
else:
    print("  !! %s" % rel)
print("=" * 52)