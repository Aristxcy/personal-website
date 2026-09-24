# 个人学术主页（GitHub Pages 版）

仿照原 Google Sites 学术主页排版的静态网站：深红页眉（右上角站内导航）、
Verdana 正文、下划线章节标题、编号论文列表。
**所有文字内容外置在 `content/*.md`（Markdown），改内容不需要碰 HTML。**

## 目录结构

```
.
├── content/            全部内容（唯一需要编辑的地方）
│   ├── home.md         首页：照片、照片说明、自我介绍
│   ├── research.md     研究：论文
│   ├── talks.md        报告 / Talks
│   ├── teaching.md     教学
│   ├── service.md      学术服务
│   └── blogs.md        博客 / PDF 笔记
├── files/              放 PDF 等附件（blogs 里链接到这里）
├── images/             所有照片都放这里（首页照片 = images/photo.svg 占位图）
├── assets/fonts/       自托管 Roboto 字体（勿动）
├── build.py            构建脚本：content/*.md → 6 个 HTML 页面
├── css/style.css       样式
├── index.html          ┐
├── blogs.html          │
├── research.html       │ 由 build.py 生成，不要直接编辑
├── talks.html          │
├── teaching.html       │
└── service.html        ┘
```

## 本地预览

```bash
python3 build.py            # 修改 content 后重新生成页面
python3 -m http.server 8000 # 浏览器打开 http://localhost:8000
```

## 修改内容

编辑 `content/` 下对应的 `.md` 文件，然后运行 `python3 build.py`，
提交并推送后 GitHub Pages 自动更新。

Markdown 语法约定：

- `## 标题`：章节标题（自动生成页内目录导航窗）
- `1. [**论文标题**(链接)](https://...)`：编号论文条目；
  下一行缩进 + `- ` 的条目渲染为小字方块项目符号（作者、期刊、备注）
- `- 条目`：普通项目符号列表（如 Teaching / Service）
- `> 注释`：章节标题下的小字注释
- `**加粗**`、`[文字](网址)`：行内加粗与链接
- `$...$`：行内数学公式（MathJax 渲染），如 `$O(\sqrt{T})$`
- 首页第一行 `![说明](图片路径)` 是照片，第二行是照片说明，
  之后各段为自我介绍（桌面端左照片、右介绍两栏）
- 内页右缘居中的图标按钮：鼠标悬停展开章节目录

### 在 Blogs 添加 PDF

1. 把 PDF 放进 `files/` 目录（例如 `files/notes-2026.pdf`）；
2. 在 `content/blogs.md` 追加：

   ```markdown
   ## 笔记标题
   2026-09-24 · [PDF](files/notes-2026.pdf)

   一两句简介。
   ```

3. `python3 build.py` 后提交推送。

### 替换照片

把自己的照片放进 `images/` 目录（例如 `images/photo.jpg`），
修改 `content/home.md` 第一行为 `![Photo](images/photo.jpg)` 后重新构建。

## 部署到 GitHub Pages

仓库已推送至 `github.com/Aristxcy/personal-website`。
若尚未开启 Pages：仓库 **Settings → Pages → Source: Deploy from a branch**，
Branch 选 `main`、目录 `/ (root)`。
站点地址：https://aristxcy.github.io/personal-website/

日常更新流程：改 `content/*.md` → `python3 build.py` → `git add -A && git commit && git push`。
