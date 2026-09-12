# xiao小小阳的个人主页

首页：<https://huoxingrnana.github.io/xiaoyang/>
全部作品：<https://huoxingrnana.github.io/xiaoyang/works.html>

Minecraft 动画 UP 主「xiao小小阳」的个人主页，纯静态站点，由 GitHub Pages 托管（源：`main` 分支根目录）。

## 页面

### `index.html`（首页）

- **首屏**：头像、打字机自我介绍、B 站数据（粉丝 / 视频 / 获赞）
- **关于我** · **技能面板** · **成就列表**
- **作品展示**：内嵌播放器 +「◀ 上一个 / 下一个 ▶」按钮，可在全部 12 个作品间来回切换；
  下面只列最新 6 个封面（点封面即切到播放器），按钮「查看全部 12 个作品 →」进第二页
- **找到我**：B 站主页 / 粉丝群（暂未开放）
- 支持**暗色模式**（跟随系统）、**分享卡片**（OG / Twitter Card）、草方块 favicon

### `works.html`（全部作品页）

- 12 个作品卡片（封面 + 时长 + 播放量），点封面去 B 站播放
- 顶部「← 返回首页」

## 更新方式

```bash
python3 upload.py     # 本地改完，传到 GitHub
python3 refresh.py    # 自动拉 B 站数据刷新两页（视频、粉丝、点赞、更新日期）
```

`refresh.py` 只改 `<!-- VIDEOS-DATA-START -->` 里的视频数据和 `data-stat="..."` 标记的数字，
不动其他内容；网络不通或被 B 站风控时会安全退出，不修改任何文件。

## 文件

| 文件 | 说明 |
|---|---|
| `index.html` | 首页本体（单文件，内联 CSS / JS） |
| `works.html` | 全部作品页 |
| `avatar.jpg` | 头像（287 x 269） |
| `og.jpg` | 分享大图（1200 x 630，微信 / QQ / B 站分享预览用） |
| `upload.py` | 部署脚本（GitHub Contents API，自动跟随仓库改名） |
| `refresh.py` | 数据自动更新脚本 |