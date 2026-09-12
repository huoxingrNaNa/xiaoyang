# xiao小小阳的个人主页

线上地址：<https://huoxingrnana.github.io/xiaoyang/>

Minecraft 动画 UP 主「xiao小小阳」的个人主页。纯静态单页面（`index.html`）+ 头像（`avatar.jpg`），
由 GitHub Pages 托管（源：`main` 分支根目录）。

## 页面内容

- **首屏**：头像、打字机自我介绍、B 站数据（粉丝 / 视频 / 获赞）
- **关于我** · **技能面板** · **成就列表**
- **作品展示**：B 站最新 6 个视频卡片（封面 + 时长 + 播放量，点击跳转）
- **找到我**：B 站主页 / 粉丝群（暂未开放）/ B 站私信

## 更新方式

本地改完 `index.html` 后，运行部署脚本即可：

```bash
python3 upload.py
```

脚本会先查仓库真实名字（改名也能跟上），再把目录下的页面文件逐个上传。

## 文件说明

| 文件 | 说明 |
|---|---|
| `index.html` | 页面本体（单文件，内联 CSS / JS，无外部依赖） |
| `avatar.jpg` | 头像（287 x 269） |
| `upload.py` | 部署脚本（GitHub Contents API） |
