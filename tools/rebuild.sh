#!/bin/sh
# xiaoyang 页面重建脚本（幂等）
# 只跑「注入类」补丁；一次性补丁（v3~v6 / v10 / v12 / v13 / v16）已固化进模板或改的是旧锚点，
# 重复跑会报错，所以这里不包含它们。
#
# 用法：
#   sh tools/rebuild.sh                 # 默认工作目录 /root/websrc
#   sh tools/rebuild.sh /path/to/site   # 指定工作目录（需自行改补丁里的 DIR 常量）

DIR=${1:-/root/websrc}
cd "$DIR" || { echo "错误：找不到工作目录 $DIR"; exit 1; }

TS=$(date +%Y%m%d-%H%M%S)
echo "== 0) 备份 =="
for f in index.html works.html game.html; do
  cp "$f" "$f.bak_rebuild_$TS" && echo "   $f -> $f.bak_rebuild_$TS"
done

run() {
  echo "== $1 =="
  python3 "$2" || { echo "!! $2 执行失败，已中止（备份仍在，可手动还原）"; exit 1; }
}

run "1/5 彩蛋块 (v7)"          tools/patches/patch_v7.py
run "2/5 音乐 + 工坊入口 (v8)"   tools/patches/patch_v8.py
run "3/5 访问量徽章 (v9)"       tools/patches/patch_v9.py
run "4/5 统计面板 (v11)"        tools/patches/patch_v11.py
run "5/5 PWA + 作品热度榜 (v14)" tools/patches/patch_v14.py
run "6/7 noscript + JSON-LD (v15)" tools/patches/patch_v15.py
run "7/7 状态徽章 + 后门 (v20)" tools/patches/patch_v20.py

echo "== 校验：模块标记是否各就各位 =="
python3 - "$DIR" <<'PY'
import io, os, sys
d = sys.argv[1]
mods = ['FUN-EGG-START', 'FUN-MUSIC-START', 'FUN-STATS-START', 'PWA-HEAD-START', 'NOSCRIPT-START']
ok = True
for f in ['index.html', 'works.html', 'game.html']:
    p = os.path.join(d, f)
    if not os.path.isfile(p):
        print('   %-12s 缺失' % f); ok = False; continue
    s = io.open(p, encoding='utf-8').read()
    bad = ['%s=%d' % (m.split('-')[0], s.count(m)) for m in mods if s.count(m) != 1]
    print('   %-12s %s' % (f, 'OK' if not bad else '异常 -> ' + ', '.join(bad)))
    ok = ok and not bad
si = io.open(os.path.join(d, 'index.html'), encoding='utf-8').read()
if si.count('PRESENCE-BADGE-START') != 1:
    print('   index.html   状态徽章缺失'); ok = False
print('结果：', '✓ 全部模块就位' if ok else '✗ 有模块异常，请检查上面的补丁输出')
PY

echo
echo "下一步：python3 tools/scripts/upload.py index.html works.html game.html"
