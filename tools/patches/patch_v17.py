#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# v17：彩蛋「手机适配」
#   1) 新增触屏手势：长按屏幕 1.2 秒 = 手机版「创造模式」（钻石雨 + /gamemode creative）
#      —— 原来只有键盘的 ↑↑↓↓←→←→BA，触屏设备永远触发不了
#   2) 提示条文案分端显示：电脑显示秘籍键位，触屏显示「长按屏幕」
#   3) 长按触发后抑制紧随其后的 click，避免顺带挖一下方块
# 全部替换点先校验 count==1，再原子落盘
import io

P = '/root/websrc/fun_egg.html'

CSS_OLD = '</style>'
CSS_NEW = '''  /* ---- v17：提示条分端文案 ---- */
  #egg-hint .hint-mob{display:none}
  html.is-touch #egg-hint .hint-pc{display:none}
  html.is-touch #egg-hint .hint-mob{display:inline}
</style>'''

H_OLD = '· 试试 ↑↑↓↓←→←→BA</div>'
H_NEW = ('· <span class="hint-pc">试试 ↑↑↓↓←→←→BA</span>'
         '<span class="hint-mob">长按屏幕 1.2 秒有惊喜</span></div>')

CLICK_OLD = ("  document.addEventListener('click', function (e) {\n"
             "    var c = ac(); if (c && c.state === 'suspended') { try { c.resume(); } catch (e) {} }\n"
             "    var t = e.target;")

CLICK_NEW = ("  document.addEventListener('click', function (e) {\n"
             "    if (pressFired) { pressFired = false; return; }   /* v17：长按彩蛋刚触发，忽略这次点击 */\n"
             "    var c = ac(); if (c && c.state === 'suspended') { try { c.resume(); } catch (e) {} }\n"
             "    var t = e.target;")

PRESS = r'''  /* ---------- v17 触屏：长按 1.2 秒 = 手机版「创造模式」 ---------- */
  var pressTimer = null;
  var pressX = 0;
  var pressY = 0;
  var pressFired = false;
  function isTouchDevice() { return ('ontouchstart' in window) || (navigator.maxTouchPoints > 0); }
  if (isTouchDevice()) { document.documentElement.className += ' is-touch'; }
  function cancelPress() { if (pressTimer) { clearTimeout(pressTimer); pressTimer = null; } }
  document.addEventListener('touchstart', function (e) {
    if (e.touches.length !== 1) { cancelPress(); return; }
    var t = e.target;
    if (t && t.closest && t.closest('a,button,#egg-hint,#egg-mus,#egg-stats,#egg-sp,.egg-ach')) return;
    pressX = e.touches[0].clientX;
    pressY = e.touches[0].clientY;
    cancelPress();
    pressTimer = setTimeout(function () {
      pressTimer = null;
      pressFired = true;
      if (window.getSelection) { try { window.getSelection().removeAllRanges(); } catch (err) {} }
      if (navigator.vibrate) { try { navigator.vibrate([12, 40, 12]); } catch (err) {} }
      sfxGem();
      creative();
    }, 1200);
  }, { passive: true });
  document.addEventListener('touchmove', function (e) {
    if (!pressTimer) return;
    if (!e.touches[0]) { cancelPress(); return; }
    if (Math.abs(e.touches[0].clientX - pressX) > 12 || Math.abs(e.touches[0].clientY - pressY) > 12) cancelPress();
  }, { passive: true });
  document.addEventListener('touchend', function () { cancelPress(); }, { passive: true });
  document.addEventListener('touchcancel', function () { cancelPress(); pressFired = false; }, { passive: true });

  /* ---------- 提示条 ---------- */'''

TIP_OLD = '  /* ---------- 提示条 ---------- */'

CONSOLE_OLD = "'%c彩蛋：↑↑↓↓←→←→BA  或按 F3'"
CONSOLE_NEW = "'%c彩蛋：↑↑↓↓←→←→BA / F3 / 手机长按屏幕 1.2 秒'"

PAIRS = [
    (CSS_OLD, CSS_NEW),
    (H_OLD, H_NEW),
    (CLICK_OLD, CLICK_NEW),
    (TIP_OLD, PRESS),
    (CONSOLE_OLD, CONSOLE_NEW),
]

s = io.open(P, encoding='utf-8').read()

if 'pressFired' in s and 'is-touch' in s:
    print('fun_egg.html 已是 v17 版本，无需改动')
    raise SystemExit(0)

if s.count('</style>') != 1:
    raise SystemExit('!! </style> 出现 %d 次（应为 1 次），结构不符预期' % s.count('</style>'))

out = s
for idx, (old, new) in enumerate(PAIRS, 1):
    c = out.count(old)
    if c != 1:
        raise SystemExit('!! 第 %d 个替换点匹配 %d 次（应为 1 次），已中止，未写入' % (idx, c))
    out = out.replace(old, new)

# 自检
for need in ['is-touch', 'pressFired', 'hint-mob', 'navigator.vibrate']:
    if need not in out:
        raise SystemExit('!! 自检失败：缺少 %s' % need)
if out.count("<script>") != s.count("<script>"):
    raise SystemExit('!! 脚本块数量异常')

io.open(P + '.bak_v17', 'w', encoding='utf-8').write(s)
io.open(P, 'w', encoding='utf-8').write(out)
print('fun_egg.html 已升级 -> %d 字节（共改动 %d 处，备份 fun_egg.html.bak_v17）'
      % (len(out.encode('utf-8')), len(PAIRS)))
print('done')