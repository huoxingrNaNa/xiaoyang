#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# xiaoyang 主页 v4：
#  1) 去掉「B 站私信」按钮
#  2) 作品区：内嵌播放器 + 上一个/下一个 切换按钮（数据驱动，可自动更新）
#  3) 暗色模式（prefers-color-scheme）
#  4) 分享大图 og.jpg（1200x630）
import io, json, shutil, time

SRC = "/root/websrc/index.html"
VID = "/root/bili_videos.json"

shutil.copy(SRC, SRC + ".bak_v4")
s = io.open(SRC, encoding="utf-8").read()
before = len(s)


def rep(old, new, tag):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit("[%s] 匹配 %d 次，中止" % (tag, n))
    s = s.replace(old, new, 1)
    print("[%s] ok" % tag)


# ---------- 1. 统计数字加 data-stat（供自动更新定位） ----------
for n, key in (("47", "fans"), ("12", "videos"), ("169", "likes")):
    rep('<span class="stat-num">%s</span>' % n,
        '<span class="stat-num" data-stat="%s">%s</span>' % (key, n),
        "1-统计-%s" % key)

rep('<p class="hero-updated">数据更新于 2026-09-12 · 共 12 个作品</p>',
    '<p class="hero-updated">数据更新于 <span data-stat="updated">2026-09-12</span>'
    ' · 共 <span data-stat="videos">12</span> 个作品</p>',
    "1-更新日期")

# ---------- 2. 作品区：播放器 + 数据 ----------
d = json.load(io.open(VID, encoding="utf-8"))
items = (d.get("data") or {}).get("item") or []
total = (d.get("data") or {}).get("count") or len(items)

vids = []
for v in items:  # 接口本身就是最新在前
    dur = v.get("duration") or 0
    vids.append({
        "bvid": v["bvid"],
        "title": v["title"],
        "cover": v["cover"].replace("http://", "https://") + "@480w_300h_1c.webp",
        "play": v.get("play") or 0,
        "dur": "%d:%02d" % (dur // 60, dur % 60),
        "date": time.strftime("%Y-%m-%d", time.localtime(v["ctime"])) if v.get("ctime") else "",
    })
blob = json.dumps(vids, ensure_ascii=False, separators=(",", ":"))

section = """<section class="panel" id="works">
    <h2 class="panel-title">
      <span class="icon">📺</span>作品展示 <span class="count-tag" data-stat="videos">%d</span>
    </h2>

    <!-- VIDEOS-DATA-START（自动更新脚本只改这一段） -->
    <script id="video-data" type="application/json">%s</script>
    <!-- VIDEOS-DATA-END -->

    <div class="player-wrap">
      <div class="player-box">
        <iframe id="vplayer" title="作品播放器" scrolling="no" frameborder="0"
                allowfullscreen="true" allow="autoplay; fullscreen; encrypted-media"></iframe>
      </div>
      <div class="player-ctrl">
        <button class="mc-btn green" id="vprev" type="button">◀ 上一个</button>
        <div class="player-info">
          <span class="player-index" id="vindex">第 1 / %d 个作品</span>
          <span class="player-title" id="vtitle"></span>
        </div>
        <button class="mc-btn green" id="vnext" type="button">下一个 ▶</button>
      </div>
      <p class="player-tip">
        点下面的封面可以直接切换到这里播放 ·
        <a id="vopen" href="#" target="_blank" rel="noopener">在 B 站打开 ↗</a>
      </p>
    </div>

    <div class="video-grid" id="video-grid"></div>
  """ % (total, blob, total)

s_works = s.index('<section class="panel" id="works">')
e_works = s.index("</section>", s_works)
s = s[:s_works] + section + s[e_works:]
print("[2-作品区] ok（%d 个视频数据）" % len(vids))

# ---------- 3. 去掉 B 站私信按钮 ----------
rep("""      <a class="mc-btn" href="https://message.bilibili.com/#/whisper/mid1452804418" target="_blank" rel="noopener">📮 B 站私信</a>
""", "", "3-移除私信按钮")

# ---------- 4. og 大图 ----------
rep('<meta property="og:image" content="https://huoxingrnana.github.io/xiaoyang/avatar.jpg">',
    '<meta property="og:image" content="https://huoxingrnana.github.io/xiaoyang/og.jpg">',
    "4-og:image")
rep('<meta property="og:image:width" content="287">',
    '<meta property="og:image:width" content="1200">', "4-og宽")
rep('<meta property="og:image:height" content="269">',
    '<meta property="og:image:height" content="630">', "4-og高")
rep('<meta name="twitter:image" content="https://huoxingrnana.github.io/xiaoyang/avatar.jpg">',
    '<meta name="twitter:image" content="https://huoxingrnana.github.io/xiaoyang/og.jpg">',
    "4-twitter图")

# ---------- 5. CSS：播放器 + 暗色模式 ----------
CSS = """  /* ===================== 播放器 ===================== */
  .player-wrap {
    margin-bottom: 24px;
  }

  .player-box {
    position: relative;
    aspect-ratio: 16 / 9;
    background: #101620;
    border: 3px solid #2b2b2b;
    box-shadow: 0 6px 0 rgba(0, 0, 0, 0.18);
    overflow: hidden;
  }

  .player-box iframe {
    display: block;
    width: 100%;
    height: 100%;
    border: 0;
  }

  .player-ctrl {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: 14px;
  }

  .player-ctrl .mc-btn {
    padding: 10px 18px;
    font-size: 14px;
  }

  .player-info {
    flex: 1;
    min-width: 150px;
    text-align: center;
  }

  .player-index {
    display: block;
    font-size: 12.5px;
    font-weight: 800;
    color: #5d9c3c;
  }

  .player-title {
    display: block;
    margin-top: 2px;
    font-size: 13.5px;
    font-weight: 800;
    color: #2b2b2b;
    word-break: break-all;
  }

  .player-tip {
    margin-top: 14px;
    font-size: 12px;
    font-weight: 700;
    color: #4a6b2c;
    text-align: center;
  }

  .player-tip a {
    color: #2b5c10;
  }

  .vcard.active .vthumb {
    outline: 3px solid #7cbd4b;
    outline-offset: 2px;
  }

  .vcard.active .vtitle {
    color: #3d7a16;
  }

  /* ===================== 暗色模式 ===================== */
  @media (prefers-color-scheme: dark) {
    body {
      color: #d7e1ef;
      background: linear-gradient(180deg, #070b14 0%, #10192e 45%, #1b2740 100%);
    }

    .nav {
      background: rgba(9, 13, 22, 0.9);
      border-bottom-color: #05070c;
      box-shadow: 0 5px 0 rgba(0, 0, 0, 0.5);
    }

    .nav-links a { color: #a6b4c8; }
    .nav-links a:hover { color: #fff; background: #2b3purple; }
    .nav-links a:hover { background: #2b3444; }

    .panel {
      background: #222a37;
      border-color: #090c12;
      box-shadow: inset 4px 4px 0 #2f3a4b, inset -4px -4px 0 #161c27, 0 10px 0 rgba(0, 0, 0, 0.5);
    }

    .panel-title {
      color: #eaf2ff;
      text-shadow: 1px 1px 0 #0a0e15;
      border-bottom-color: #3b4658;
      box-shadow: 0 3px 0 #2b3444;
    }

    .panel p { color: #c3cee0; }

    .highlight {
      color: #d8f8b4;
      background: rgba(124, 189, 75, 0.22);
      border-bottom-color: #4f7a33;
    }

    .hero-name {
      color: #f4f8ff;
      text-shadow: 3px 3px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000,
                   0 10px 26px rgba(0, 0, 0, 0.6);
    }

    .hero-role { color: #b6e596; text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.65); }
    .caret { background: #b6e596; }

    .hero-avatar img { background: #1b2231; border-color: #090c12; }

    .stat {
      background: rgba(26, 33, 46, 0.92);
      border-color: #090c12;
      box-shadow: inset 3px 3px 0 rgba(255, 255, 255, 0.07), inset -3px -3px 0 rgba(0, 0, 0, 0.45),
                  0 5px 0 rgba(0, 0, 0, 0.5);
    }

    .stat-num { color: #a8e57d; }
    .stat-label { color: #9fb0c5; }
    .hero-updated { color: #b6e596; text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.6); }

    .skill-head { color: #dde7f4; }
    .skill-head span:last-child { color: #a8e57d; }

    .bar {
      background: #39434f;
      border-color: #090c12;
      box-shadow: inset 2px 2px 0 #262d38;
    }

    .ach {
      background: #1d2531;
      border-color: #090c12;
      box-shadow: inset 3px 3px 0 #2b3purple, inset -3px -3px 0 #131922;
    }

    .ach { box-shadow: inset 3px 3px 0 #2b3purple; }
    .ach { box-shadow: inset 3px 3px 0 #2c3746, inset -3px -3px 0 #131922; }
    .ach:hover { background: #253040; }
    .ach-title { color: #ffe97a; }
    .ach-desc { color: #9fb0c5; }

    .vtitle { color: #e8f0fb; }
    .vmeta { color: #a8e57d; }
    .vcard.active .vtitle { color: #a8e57d; }

    .vthumb {
      background: #2a3purple;
      border-color: #090c12;
      box-shadow: inset 3px 3px 0 rgba(255, 255, 255, 0.07), inset -3px -3px 0 rgba(0, 0, 0, 0.5),
                  0 5px 0 rgba(0, 0, 0, 0.45);
    }

    .vthumb { background: #2a3342; }

    .player-box { background: #0b1017; border-color: #090c12; }
    .player-title { color: #e8f0fb; }
    .player-index { color: #a8e57d; }
    .player-tip { color: #9fc47f; }
    .player-tip a { color: #cdf7a8; }

    .mc-btn { border-color: #05070c; }

    footer { color: #9ec27f; text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.6); }
    footer .line { background: #4f7a33; border-color: #090c12; }
  }

"""
rep("</style>", CSS + "</style>", "5-CSS")

# ---------- 6. JS：暗色粒子 + 播放器逻辑 ----------
rep('  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;',
    '  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;\n'
    '  var DARK = window.matchMedia("(prefers-color-scheme: dark)").matches;\n'
    '\n'
    '  if (window.matchMedia) {\n'
    '    var mq = window.matchMedia("(prefers-color-scheme: dark)");\n'
    '    var onScheme = function (e) { DARK = e.matches; initParticles(); };\n'
    '    if (mq.addEventListener) { mq.addEventListener("change", onScheme); }\n'
    '    else if (mq.addListener) { mq.addListener(onScheme); }\n'
    '  }',
    "6-暗色检测")

rep('tint: Math.random() > 0.78 ? "#7cbd4b" : "#ffffff"',
    'tint: Math.random() > 0.78 ? (DARK ? "#39d353" : "#7cbd4b") : (DARK ? "#cfe6ff" : "#ffffff")',
    "6-粒子配色")

PLAYER_JS = """
  /* ================= 作品数据渲染 + 播放器 ================= */
  (function () {
    var dataEl = document.getElementById("video-data");
    var grid = document.getElementById("video-grid");
    var player = document.getElementById("vplayer");
    var idxEl = document.getElementById("vindex");
    var titleEl = document.getElementById("vtitle");
    var openEl = document.getElementById("vopen");
    var prevBtn = document.getElementById("vprev");
    var nextBtn = document.getElementById("vnext");
    var videos = [];
    var current = 0;

    try { videos = JSON.parse(dataEl.textContent) || []; } catch (e) { videos = []; }

    if (!videos.length) {
      if (grid) { grid.innerHTML = '<p style="font-size:14px;font-weight:700;">作品整理中…</p>'; }
      return;
    }

    function videoUrl(v) {
      return "https://player.bilibili.com/player.html?bvid=" + v.bvid +
             "&page=1&high_quality=1&danmaku=0&autoplay=1";
    }

    function highlight() {
      if (!grid) { return; }
      for (var i = 0; i < grid.children.length; i++) {
        var el = grid.children[i];
        el.className = (el.getAttribute("data-i") === String(current)) ? "vcard active" : "vcard";
      }
    }

    function show(i, play) {
      current = (i % videos.length + videos.length) % videos.length;
      var v = videos[current];
      if (player) { player.src = play ? videoUrl(v) : videoUrl(v).replace("autoplay=1", "autoplay=0"); }
      if (idxEl) { idxEl.textContent = "第 " + (current + 1) + " / " + videos.length + " 个作品"; }
      if (titleEl) { titleEl.textContent = v.title; }
      if (openEl) { openEl.href = "https://www.bilibili.com/video/" + v.bvid; }
      highlight();
    }

    function buildGrid() {
      var html = "";
      for (var i = 0; i < videos.length; i++) {
        var v = videos[i];
        html += '<a class="vcard" data-i="' + i + '" href="https://www.bilibili.com/video/' + v.bvid +
                '" target="_blank" rel="noopener">' +
                '<span class="vthumb"><img src="' + v.cover + '" alt="' +
                String(v.title).replace(/"/g, "&" + "quot;") +
                '" loading="lazy" referrerpolicy="no-referrer">' +
                '<span class="vtime">' + v.dur + '</span></span>' +
                '<span class="vtitle">' + v.title + '</span>' +
                '<span class="vmeta">▶ ' + v.play + ' 次播放 · ' + v.date + '</span></a>';
      }
      grid.innerHTML = html;
      for (var k = 0; k < grid.children.length; k++) {
        grid.children[k].addEventListener("click", function (e) {
          e.preventDefault();
          show(parseInt(this.getAttribute("data-i"), 10), true);
        });
      }
    }

    if (grid) { buildGrid(); }
    show(0, false);

    if (prevBtn) { prevBtn.addEventListener("click", function () { show(current - 1, true); }); }
    if (nextBtn) { nextBtn.addEventListener("click", function () { show(current + 1, true); }); }
  })();
"""

i = s.rindex("})();")
s = s[:i] + PLAYER_JS + s[i:]
print("[6-播放器JS] ok")

io.open(SRC, "w", encoding="utf-8").write(s)
print("写入完成: %d -> %d 字符" % (before, len(s)))