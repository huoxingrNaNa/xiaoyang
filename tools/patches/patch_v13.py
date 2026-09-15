#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v13：给访问统计加「备用计数源」——abacus 不可达时自动切到 busuanzi
#   - 徽章里预置 busuanzi 的取值元素（#busuanzi_value_site_pv / _uv），默认隐藏
#   - abacus 的 5 个请求全部失败 -> 切换显示备用源 + 懒加载 busuanzi 脚本
#   - busuanzi 也拿不到 -> 整个徽章隐藏（绝不出现半截乱码）
# 所有替换点先全部校验通过，再一次性落盘（原子写入）
import io

P = '/root/websrc/stats_egg.html'
s = io.open(P, encoding='utf-8').read()

PAIRS = []

# ---------- A) 徽章 HTML：加入备用源显示位 ----------
PAIRS.append((
    '<span id="egg-stats" role="button" tabindex="0" hidden title="本站访问统计（点击看排行榜）">'
    '<span>👀 <b id="egg-pv">–</b> <span class="dv" id="egg-dy"></span></span>'
    '<span class="sep">|</span><span>🧍 <b id="egg-uv">–</b></span></span>',
    '<span id="egg-stats" role="button" tabindex="0" hidden title="本站访问统计（点击看排行榜）">'
    '<span class="ab">👀 <b id="egg-pv">–</b> <span class="dv" id="egg-dy"></span></span>'
    '<span class="fb" hidden>👀 <b id="busuanzi_value_site_pv">–</b><em>※</em></span>'
    '<span class="sep">|</span>'
    '<span class="ab">🧍 <b id="egg-uv">–</b></span>'
    '<span class="fb" hidden>🧍 <b id="busuanzi_value_site_uv">–</b><em>※</em></span></span>'
))

# ---------- B) 备用源配色 ----------
PAIRS.append((
    '#egg-stats .sep{opacity:.35}',
    '#egg-stats .sep{opacity:.35}\n'
    '#egg-stats .fb b{color:#ffd479}\n'
    '#egg-stats em{font-style:normal;opacity:.65;font-size:10px;margin-left:1px}'
))

# ---------- C) 记账逻辑：失败计数 + 触发切换 ----------
PAIRS.append((
    """  var jobs = [];
  jobs.push(ask('hit/' + NS + 'hits').then(function (j) { var v = num(j); if (v !== null) snap.pv = v; }));
  jobs.push(ask('hit/' + NS + 'd-' + today).then(function (j) { var v = num(j); if (v !== null) snap.dy = v; }));
  jobs.push(ask('hit/' + NS + 'p-' + page).then(function (j) { var v = num(j); if (v !== null) snap['p-' + page] = v; }));
  jobs.push(ask((seen ? 'get/' : 'hit/') + NS + 'visitors').then(function (j) {
    var v = num(j); if (v !== null) snap.uv = v;
    try { localStorage.setItem('xy_seen', '1'); } catch (e) {}
  }));
  jobs.push(ask((daySeen ? 'get/' : 'hit/') + NS + 'u-' + today).then(function (j) {
    var v = num(j); if (v !== null) snap.du = v;
    try { localStorage.setItem('xy_day', today); } catch (e) {}
  }));
  Promise.all(jobs).then(function () { cset('xy_snap', snap); badge(); })
    .catch(function () { badge(); });""",
    """  var okCount = 0, failCount = 0, fbActive = false;

  function account(path, apply) {
    return ask(path).then(function (j) {
      var v = num(j);
      if (v === null) throw new Error('empty');
      apply(v);
      okCount++;
    }).catch(function () { failCount++; });
  }

  var jobs = [];
  jobs.push(account('hit/' + NS + 'hits', function (v) { snap.pv = v; }));
  jobs.push(account('hit/' + NS + 'd-' + today, function (v) { snap.dy = v; }));
  jobs.push(account('hit/' + NS + 'p-' + page, function (v) { snap['p-' + page] = v; }));
  jobs.push(account((seen ? 'get/' : 'hit/') + NS + 'visitors', function (v) {
    snap.uv = v;
    try { localStorage.setItem('xy_seen', '1'); } catch (e) {}
  }));
  jobs.push(account((daySeen ? 'get/' : 'hit/') + NS + 'u-' + today, function (v) {
    snap.du = v;
    try { localStorage.setItem('xy_day', today); } catch (e) {}
  }));
  Promise.all(jobs).then(function () {
    cset('xy_snap', snap);
    if (okCount === 0) fallback(); else badge();
  });"""
))

# ---------- D) 备用源逻辑 ----------
PAIRS.append((
    '  /* ---------- 统计面板 ---------- */',
    """  /* ---------- 备用计数源（busuanzi）：主源不可达时顶上 ---------- */
  var SRC_OK = '数据来自 abacus 计数器 · 只记数字，不收集任何个人信息';
  var SRC_FB = '⚠️ 主计数源（abacus）不可达，当前显示备用源 busuanzi 的累计数；今日新增 / 排行榜需要主源，暂时不可用';

  function swapToFallback() {
    var abs = box.querySelectorAll('.ab'), fbs = box.querySelectorAll('.fb'), i;
    for (i = 0; i < abs.length; i++) abs[i].hidden = true;
    for (i = 0; i < fbs.length; i++) fbs[i].hidden = false;
    box.hidden = false;
    box.setAttribute('title', '主计数源不可达，当前显示备用源 busuanzi 的累计数（※）—— 点开看详情');
  }

  function fallback() {
    if (fbActive) return;
    fbActive = true;
    swapToFallback();
    if (!document.getElementById('egg-bsz-js')) {
      var sc = document.createElement('script');
      sc.id = 'egg-bsz-js';
      sc.async = true;
      sc.src = 'https://busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js';
      document.head.appendChild(sc);
    }
    /* busuanzi 会把数字写进 #busuanzi_value_* 元素，轮询等它填好 */
    var tries = 0;
    var t = setInterval(function () {
      tries++;
      var a = el('busuanzi_value_site_pv'), b = el('busuanzi_value_site_uv');
      var okA = !!(a && /\\d/.test(a.textContent || ''));
      var okB = !!(b && /\\d/.test(b.textContent || ''));
      if (okA || okB) { clearInterval(t); return; }
      if (tries > 25) { clearInterval(t); if (!okA && !okB) box.hidden = true; }
    }, 400);
  }

  /* ---------- 统计面板 ---------- */"""
))

# ---------- E) 面板：来源说明可切换 ----------
PAIRS.append((
    """      '<div class="sub">来自 abacus 计数器 · 只记数字，不收集任何个人信息</div>' +""",
    """      '<div class="sub">数据来自 abacus 计数器 · 只记数字，不收集任何个人信息</div>' +"""
))
PAIRS.append((
    """'<div class="sub">数据来自 abacus 计数器 · 只记数字，不收集任何个人信息</div>' +""",
    """'<div class="sub" id="egg-c-src">数据来自 abacus 计数器 · 只记数字，不收集任何个人信息</div>' +"""
))

# ---------- F) render() 里同步来源说明 ----------
PAIRS.append((
    """    set('egg-c-best', (best && best.v) ? ('最近 7 天最高：' + dash(best.d) + '（' + best.v + ' 次）')
      : '最近 7 天暂无数据');""",
    """    set('egg-c-best', (best && best.v) ? ('最近 7 天最高：' + dash(best.d) + '（' + best.v + ' 次）')
      : '最近 7 天暂无数据');
    set('egg-c-src', fbActive ? SRC_FB : SRC_OK);"""
))

# ---------- 顺序校验 + 原子落盘（先全部在内存里替换成功，才写文件） ----------
out = s
for idx, (old, new) in enumerate(PAIRS, 1):
    c = out.count(old)
    if c != 1:
        print('!! 未写入：第 %d 处锚点出现 %d 次（应为 1）：%s' % (idx, c, old[:50]))
        raise SystemExit(1)
    out = out.replace(old, new)

s = out

if 'fbActive' not in s or 'busuanzi_value_site_pv' not in s or 'egg-c-src' not in s:
    raise SystemExit('!! 自检失败，未写入')

io.open(P, 'w', encoding='utf-8').write(s)
print('OK: 备用源已接入（%d 处替换）' % len(PAIRS))
print('    stats_egg.html 现在 %d 字节' % len(s.encode('utf-8')))