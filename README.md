# 个人学术主页（GitHub Pages 版）

仿照 Google Sites 学术主页风格（深红顶栏 + 侧边抽屉导航 + 居中内容栏）的纯静态个人网站，
无需任何构建步骤，可直接托管到 GitHub Pages。

## 目录结构

```
.
├── index.html        首页：照片 + 个人简介
├── research.html     研究：论文 / 报告列表
├── teaching.html     教学与服务
├── blogs.html        博客列表
├── css/style.css     全站样式（颜色、字号等都在文件开头的 :root 里）
├── js/nav.js         汉堡菜单抽屉逻辑
└── assets/photo.svg  首页照片占位图
```

## 本地预览

```bash
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

## 部署到 GitHub Pages

1. 在 GitHub 上新建一个仓库（例如 `personal-website`），把本目录所有文件推送上去：

   ```bash
   git init
   git add .
   git commit -m "personal website"
   git branch -M main
   git remote add origin git@github.com:<你的用户名>/personal-website.git
   git push -u origin main
   ```

2. 打开仓库的 **Settings → Pages**。
3. **Source** 选择 *Deploy from a branch*，Branch 选 `main`、目录选 `/ (root)`，保存。
4. 等待 1–2 分钟，访问 `https://<你的用户名>.github.io/personal-website/`。

> 所有链接均为相对路径，放在仓库根目录或子路径下都能正常工作。
> 如需绑定自己的域名：在仓库 Settings → Pages 里填写 Custom domain，
> 并在域名 DNS 添加指向 `<你的用户名>.github.io` 的 CNAME 记录。

## 替换成自己的内容

- **名字**：每个页面 `<title>`、`.site-title`、`.drawer-title`、页脚中的 “Your Name”。
- **照片**：首页照片目前是占位图 `assets/photo.svg`（Google Sites 的图片 CDN 有防盗链，
  无法自动下载原图）。请把你自己的照片保存为 `assets/photo.jpg`，
  并把 `index.html` 中 `<img class="photo" src="assets/photo.svg">` 改为
  `src="assets/photo.jpg"`。
- **简介 / 论文 / 教学 / 博客**：直接编辑对应 HTML 里的文字；论文条目复制
  `<div class="paper">…</div>` 块即可，`*` 表示通讯作者、`^` 表示同等贡献。
- **配色**：`css/style.css` 开头 `:root` 中的 `--crimson` 等变量。
