# xiaoyang 站点工具链（tools/）

这里是**站点源码**。仓库根目录的 `index.html` / `works.html` / `game.html` 是**生成物**——
页面里的彩蛋、背景音乐、访问统计面板、PWA、作品热度榜，全部由下面的「模块模板 + 补丁脚本」注入生成。

> ⚠️ 想改页面功能，请改 `templates/` 里的模块，再跑 `tools/rebuild.sh` 重新注入。
> 直接手改根目录的 HTML 会在下一次重建时被覆盖。

---

## 目录结构

```
tools/
├── README.md                  ← 你正在看的这份
├── rebuild.sh                 ← 一键重建三个页面（幂等）
├── templates/                 ← 模块模板（纯 HTML 片段，带 MARKER 标记）
│   ├── fun_egg.html           ← 方块世界彩蛋：成就弹窗 / 粒子 / Konami 钻石雨 / F3 调试屏
│   ├── music_egg.html         ← C418 风格环境音乐（WebAudio 现场合成，右下角可开关）
│   ├── stats_egg.html         ← 访问统计：徽章 + 面板（今日新增 / 页面热度榜 / 7 天柱状图 / 双通道）
│   ├── pwa_head.html          ← PWA 头部：manifest + 图标 + Apple meta + Service Worker 注册
│   ├── works_rank.html        ← 作品热度榜：Top5 播放量榜 + 每张卡片的播放量条
│   └── presence.html          ← 状态徽章 + 状态后门面板（三源降级）
├── patches/                   ← 注入补丁（按编号顺序执行，幂等）
│   ├── patch_site_v3.py       ← 一次性：初版作品区改版
│   ├── patch_v4.py  v5  v6    ← 一次性：按钮/首屏数量/暗色背景
│   ├── patch_v7.py            ← 注入彩蛋块
│   ├── patch_music_hook.py    ← 一次性：给彩蛋块加对外接口（成就/音效）
│   ├── patch_v8.py            ← 注入音乐 + 工坊入口
│   ├── patch_v9.py            ← 注入访问量徽章
│   ├── patch_v10.py           ← 一次性：修徽章与提示条重叠（已固化进模板）
│   ├── patch_v11.py           ← 注入统计面板
│   ├── patch_v12.py           ← 一次性：逐日统计改北京时间（已固化进模板）
│   ├── patch_v13.py           ← 一次性：备用计数源（已固化进模板）
│   ├── patch_v14.py           ← 注入 PWA 头部 + 作品热度榜
│   ├── patch_v15.py           ← 注入 noscript 兜底 + 首页 JSON-LD
│   ├── patch_v16.py           ← 一次性：让 refresh.py 顺带更新 noscript 作品清单
│   ├── patch_v17.py           ← 一次性：彩蛋手机适配（长按手势 + 提示条文案分端）
│   ├── patch_v18.py           ← 一次性：提示条改按「主输入设备」判定 + 更新日期相对化
│   ├── patch_v20.py           ← 注入状态徽章 + 后门（并让 sw.js 不缓存 presence.txt）
│   └── patch_readme_v8.py     ← 一次性：README 补入口
└── scripts/                   ← 日常脚本
    ├── upload.py              ← 上传文件到 GitHub（自动读远端 sha / 跟随仓库改名）
    ├── refresh.py             ← 拉 B 站数据刷新作品卡片（GitHub Actions 每天跑）
    ├── site_stats.py          ← 查站点访问统计（abacus / busuanzi）
    └── repo_stats.py          ← 查 GitHub 仓库流量（⭐/🍴/clone，与网站访问无关）
```

---

## 注入链（当前线上页面的完整构成）

| 顺序 | 补丁 | 作用 | 目标页面 |
|---|---|---|---|
| 1 | `patch_v7.py` | 彩蛋块（成就/粒子/挖掘） | index, works |
| 2 | `patch_music_hook.py` | 彩蛋对外接口（一次性） | index, works |
| 3 | `patch_v8.py` | 背景音乐 + 工坊入口 | 三页 |
| 4 | `patch_v9.py` | 访问量徽章 | 三页 |
| 5 | `patch_v10.py` | 徽章/提示条布局（一次性） | 三页 |
| 6 | `patch_v11.py` | 统计面板（今日新增/热度榜/柱状图） | 三页 |
| 7 | `patch_v12.py` | 逐日统计统一 UTC+8（一次性） | 三页 |
| 8 | `patch_v13.py` | 备用计数源 busuanzi（一次性） | 三页 |
| 9 | `patch_v14.py` | PWA 头部 + 作品热度榜 | 三页 / works |
| 10 | `patch_v15.py` | noscript 兜底 + JSON-LD | 三页 / index |
| 11 | `patch_v16.py` | refresh.py 同步 noscript 清单（一次性） | refresh.py |

**标记约定**：每个模块用 `<!-- XXX-START --> ... <!-- XXX-END -->` 包住。
补丁幂等规则 = 有标记就替换标记之间的内容，没有就插在 `</body>`（页面模块）或 `</head>`（头部模块）之前。

---

## 一次性补丁（已生效，**不要重跑**）

`patch_site_v3` / `v4` / `v5` / `v6` / `v10` / `v12` / `v13` / `patch_music_hook` / `patch_readme_v8` / `patch_v16` / `patch_v17` / `patch_v18` / `patch_v20`

原因：它们改的是**当时那份 HTML 的局部文本**，锚点如今已被后续补丁改写；
或者结果**已经固化进 `templates/`**（例如 v10 的布局修正、v12 的 `ymdCN`、v13 的 `fbActive` 都已经在模板里了）。
重复运行可能因锚点消失而报错或重复修改。

---

## 🔐 状态后门怎么用（v20）

**入口**：首页 hero 里的状态徽章 → **2 秒内连点 5 下** 打开设置面板；也可在网址后加 `#admin`。

**能改什么**：在线 / 做动画中 / 忙碌 / 睡觉中 / 离线，外加一句附言（≤40 字），或「恢复自动」。

**数据存在哪（三源降级）**：

| 优先级 | 源 | 说明 |
|---|---|---|
| 1️⃣ | `ntfy.sh/<TOPIC>` | 后门写入的通道，秒级生效。**TOPIC 就是钥匙**，写在 `templates/presence.html` 里，改了等于换钥匙 |
| 2️⃣ | `presence.txt` | 仓库根目录的备用文件。后门面板提示「网络不通」时，用手机 GitHub 改这个文件（一行 `状态\|附言`，`#` 开头是注释） |
| 3️⃣ | 按北京时间自动 | 07:30–22:30 = 在线，其余 = 睡觉中（时段写在 `presence.html` 的 `SCHED`）。永远有兜底 |

**诚实的限制**：静态站**做不到真正的「在线/离线检测」**（没有服务器盯着你）。
线上真正存在的只有「手动状态」+「按时段猜」，所以这个设计＝手动为主、自动兜底。
另外后门只是「隐蔽入口」，不是安全边界：**能读页面源码的人就能找到通道名**，
最坏情况是有人乱改你的状态显示（改回去就行）。真需要严格权限就得上带后端的方案。

## 日常操作

```sh
# 重建三个页面（幂等，会自动备份 .bak_rebuild_时间戳）
sh tools/rebuild.sh

# 部署（文件名可写多个）
python3 tools/scripts/upload.py index.html works.html

# 看站点访问统计（默认最近 30 天）
python3 tools/scripts/site_stats.py 90

# 看仓库流量
python3 tools/scripts/repo_stats.py
```

**脚本里的 GitHub Token 已移除**，改为读环境变量：

```sh
export GITHUB_TOKEN=ghp_xxxxxxxx
```

---

## 加一个新模块的标准流程

1. `templates/xxx.html`：整块内容用 `<!-- XXX-START -->` / `<!-- XXX-END -->` 包住
2. `patches/patch_vNN.py`：**先全部校验 count==1，再原子落盘**（不要边匹配边写文件，写坏了没法回滚）
3. `rebuild.sh` 末尾追加一行调用
4. 校验：抽出的 JS 过 `node --check`，Python 过 `python3 -m py_compile`
5. 部署后 `sleep 85` 再验线上（GitHub Pages 构建有延迟），grep 标记确认生效

---

## 踩坑记录 / 注意事项

- **统计键**：主源 abacus，命名空间 `xiaoyang-site`；键为 `hits`(累计PV) / `visitors`(UV) / `d-YYYYMMDD`(每日PV) / `u-YYYYMMDD`(每日UV) / `p-index`·`p-works`·`p-game`(分页)。
- **日期一律按北京时间 UTC+8 分桶**（前端 `ymdCN()`，脚本 `timezone(timedelta(hours=8))`）。海外访客否则会把同一天拆到不同日期键上，逐日榜就永久不准。
- **备用源 busuanzi 按「域名」统计**，数字与主源天生不同，界面上用黄色 + `※` 区分；它只在主源失败时才懒加载，正常访客一个多余请求都不发。
- **`sw.js` 缓存**：换了图标 / manifest / 预缓存清单后，必须把 `VER` 加一，否则老访客一直吃旧缓存。
- **`404.html` 必须放仓库根目录**（GitHub Pages 的约定），不能用子目录。
- **`robots.txt` 对项目页作用有限**：爬虫规范上只读域名根 `https://huoxingrnana.github.io/robots.txt`，而项目页在 `/xiaoyang/` 下，所以这里的 robots.txt 更像一份声明，**sitemap 的作用更实际**。
- **彩蛋的手机适配（v17）**：触屏设备没有键盘，所以「创造模式」钻石雨改用手势触发 —— **长按屏幕 1.2 秒**（移动超过 12px 或落在按钮/链接上会取消，不会影响滑动与点击）；提示条文案按 `html.is-touch` 分端显示（电脑给键位、手机给手势）。
- **日期口径（v18）**：`refresh.py` 统一按**北京时间 UTC+8** 取年月日（`ymd_cn()`），与站点统计口径一致；同时写入 `<span data-at="2026-09-17T00:19:33+08:00">` 机器可读时间戳，页面用 JS 显示成「X 小时前」。这样即使 GitHub 定时任务排队延后（本仓库实测晚 5 小时左右），页面看着也不会「过期」。
- **提示条分端判定（v18）**：必须用 CSS 媒体查询 `(hover: none), (pointer: coarse)` 判断主输入设备；**不要**用 JS 的 `ontouchstart` / `maxTouchPoints` —— 触屏笔记本（有鼠标也有触摸屏）会被误判成手机，导致电脑上显示「长按屏幕」而不是箭头秘籍。
- **GitHub 定时任务不准点**：`update.yml` 里写的 cron 只是「排队时间」，实测本仓库延迟 5 小时以上，所以任何依赖「定时任务运行时刻」的显示逻辑都不可靠，要用相对时间。
- **补丁里的 `DIR` 硬编码为 `/root/websrc`**（沙箱路径）。换环境后需要先改这些常量，或用 `sh tools/rebuild.sh <工作目录>`。
- **沙箱不是保险箱**：本目录就是为此存在的——页面成品在 GitHub，源码在这里也有一份。

---

## 安全

- 归档进仓库的脚本**不含任何 Token**（读 `GITHUB_TOKEN` 环境变量）。
- 曾经在沙箱脚本里出现过明文 Token，建议**在 GitHub 设置里轮换一次**（Settings → Developer settings → Personal access tokens），然后更新本地环境变量即可。
