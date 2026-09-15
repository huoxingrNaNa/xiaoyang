#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xiaoyang 主页改版 v3：
#  1) 作品展示区：真实 B 站视频卡片（取最新 6 个）
#  2) 修复死链：粉丝群→暂未开放（禁用态）；邮箱→B 站私信
#  3) 分享卡片：description / OG / Twitter Card / 草方块 favicon
#  4) 首屏加“数据更新于”说明
import io, json, shutil, time

SRC = "/root/websrc/index.html"
VID = "/sdcard/bili_videos.json"
BASE = "https://huoxingrnana.github.io/xiaoyang/"
SPACE = "https://space.bilibili.com/1452804418"

shutil.copy(SRC, SRC + ".bak_v3")
s = io.open(SRC, encoding="utf-8").read()
before = len(s)


def rep(old, new, tag):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit("[%s] 匹配 %d 次，中止（文件未改）" % (tag, n))
    s = s.replace(old, new)
    print("[%s] ok" % tag)


# ---------- 1. 头部 meta / 分享卡片 / favicon ----------
DESC = ("xiao小小阳 —— 来自海南的 Minecraft 动画 UP 主，"
        "「BBS 动画小练习」系列作者。这里有我的作品、技能面板和联系方式。")
FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E"
           "%3Crect width='16' height='16' fill='%238b5a2b'/%3E"
           "%3Crect width='16' height='7' fill='%237cbd4b'/%3E"
           "%3Crect y='5' width='16' height='2' fill='%235d9c3c'/%3E%3C/svg%3E")

META = """<title>xiao小小阳 · 我的世界</title>
<meta name="description" content="%s">
<meta name="author" content="xiao小小阳">
<meta name="theme-color" content="#5fb8f5">
<link rel="canonical" href="%s">
<link rel="icon" href="%s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="xiao小小阳的个人主页">
<meta property="og:title" content="xiao小小阳 · 我的世界">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:image" content="%savatar.jpg">
<meta property="og:image:width" content="287">
<meta property="og:image:height" content="269">
<meta property="og:locale" content="zh_CN">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="xiao小小阳 · 我的世界">
<meta name="twitter:description" content="%s">
<meta name="twitter:image" content="%savatar.jpg">""" % (DESC, BASE, FAVICON, DESC, BASE, BASE, DESC, BASE)

rep('<title>xiao小小阳 · 我的世界</title>', META, "1-头部meta")

# ---------- 2. 首屏加“数据更新于” ----------
rep("""        <span class="stat-num">169</span>
        <span class="stat-label">获赞</span>
      </div>
    </div>""",
    """        <span class="stat-num">169</span>
        <span class="stat-label">获赞</span>
      </div>
    </div>
    <p class="hero-updated">数据更新于 %s · 共 %d 个作品</p>"""
    % (time.strftime("%Y-%m-%d"), (json.load(io.open(VID, encoding="utf-8"))["data"]["count"])),
    "2-数据更新说明")

# ---------- 3. 作品展示区 ----------
d = json.load(io.open(VID, encoding="utf-8"))
items = (d.get("data") or {}).get("item") or []
total = (d.get("data") or {}).get("count") or len(items)
show = items[:6]

cards = []
for v in show:
    bvid = v["bvid"]
    title = v["title"].replace('"', "&" + "quot;")
    cover = v["cover"].replace("http://", "https://") + "@480w_300h_1c.webp"
    dur = v.get("duration") or 0
    dur_txt = "%d:%02d" % (dur // 60, dur % 60)
    date = time.strftime("%Y-%m-%d", time.localtime(v["ctime"])) if v.get("ctime") else ""
    play = v.get("play") or 0
    cards.append("""      <a class="vcard" href="https://www.bilibili.com/video/%s" target="_blank" rel="noopener">
        <span class="vthumb">
          <img src="%s" alt="%s" loading="lazy" referrerpolicy="no-referrer">
          <span class="vtime">%s</span>
        </span>
        <span class="vtitle">%s</span>
        <span class="vmeta">▶ %s 次播放 · %s</span>
      </a>""" % (bvid, cover, title, dur_txt, title, play, date))
grid = "\n".join(cards)

s_works = s.index('<section class="panel" id="works">')
e_works = s.index("</section>", s_works)
new_works = """<section class="panel" id="works">
    <h2 class="panel-title">
      <span class="icon">📺</span>作品展示 <span class="count-tag">%d</span>
    </h2>

    <div class="video-grid">
%s
    </div>

    <div class="works-more">
      <a class="mc-btn green" href="%s/video" target="_blank" rel="noopener">在 B 站看全部 %d 个作品 →</a>
    </div>
  """ % (total, grid, SPACE, total)
s = s[:s_works] + new_works + s[e_works:]
print("[3-作品区] ok（%d 个卡片 / 共 %d 个作品）" % (len(show), total))

# ---------- 4. 联系方式死链 ----------
rep("""      <a class="mc-btn" href="#">💬 粉丝群</a>
      <a class="mc-btn" href="#">📮 邮箱</a>""",
    """      <span class="mc-btn disabled" title="暂未开放">💬 粉丝群 · 暂未开放</span>
      <a class="mc-btn" href="https://message.bilibili.com/#/whisper/mid1452804418" target="_blank" rel="noopener">📮 B 站私信</a>""",
    "4-联系方式")

# ---------- 5. 新增 CSS ----------
CSS = """  /* ===================== 数据更新说明 ===================== */
  .hero-updated {
    margin-top: 16px;
    font-size: 12.5px;
    font-weight: 700;
    color: #1e4a08;
    text-shadow: 1px 1px 0 rgba(255, 255, 255, 0.55);
    opacity: 0.9;
  }

  /* ===================== 作品卡片 ===================== */
  .count-tag {
    padding: 2px 9px;
    font-size: 12px;
    font-weight: 800;
    color: #fff;
    background: #7cbd4b;
    border: 2px solid #2b2b2b;
    box-shadow: inset 2px 2px 0 rgba(255, 255, 255, 0.4);
  }

  .video-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(215px, 1fr));
    gap: 16px;
  }

  .vcard {
    display: block;
    text-decoration: none;
    transition: transform 0.16s ease, filter 0.16s ease;
  }

  .vcard:hover {
    transform: translateY(-4px);
    filter: brightness(1.03);
  }

  .vthumb {
    position: relative;
    display: block;
    aspect-ratio: 16 / 9;
    background: #8b8b8b;
    border: 3px solid #2b2b2b;
    box-shadow: inset 3px 3px 0 rgba(255, 255, 255, 0.25),
                inset -3px -3px 0 rgba(0, 0, 0, 0.22),
                0 5px 0 rgba(0, 0, 0, 0.16);
    overflow: hidden;
  }

  .vthumb img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .vtime {
    position: absolute;
    right: 5px;
    bottom: 5px;
    padding: 1px 6px;
    font-size: 11px;
    font-weight: 800;
    color: #fff;
    background: rgba(0, 0, 0, 0.72);
    border: 2px solid #1a1a1a;
  }

  .vtitle {
    display: block;
    margin-top: 9px;
    font-size: 13.5px;
    font-weight: 800;
    line-height: 1.5;
    color: #2b2b2b;
  }

  .vmeta {
    display: block;
    margin-top: 3px;
    font-size: 11.5px;
    font-weight: 700;
    color: #5d9c3c;
  }

  .works-more {
    margin-top: 24px;
    text-align: center;
  }

  .mc-btn.disabled {
    opacity: 0.55;
    cursor: not-allowed;
    filter: grayscale(0.35);
  }

  .mc-btn.disabled:hover {
    background: #6f6f6f;
    box-shadow: inset 3px 3px 0 #9a9a9a, inset -3px -3px 0 #4a4a4a;
  }

"""
rep("  /* ===================== 响应式 ===================== */",
    CSS + "  /* ===================== 响应式 ===================== */",
    "5-新增CSS")

# ---------- 6. 小屏微调 ----------
rep("""  @media (max-width: 560px) {
    .logo span:last-child { font-size: 15px; }""",
    """  @media (max-width: 560px) {
    .logo span:last-child { font-size: 15px; }
    .video-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; }
    .vtitle { font-size: 12.5px; }""",
    "6-响应式")

io.open(SRC, "w", encoding="utf-8").write(s)
print("写入完成: %d -> %d 字节" % (before, len(s)))
print("文件: %s" % SRC)