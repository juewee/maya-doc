# Maya Command Documentation

Maya Python 命令文档爬虫与浏览器，支持 Maya 2020 / 2022 / 2025 三个版本。

## 项目结构

```
maya_doc/
├── scraper.js            # 命令详情爬虫
├── scrape_cats.js        # 分类索引爬虫
├── server.js             # 本地浏览服务器（含代理端点）
├── browse.html           # 命令浏览器 UI
├── package.json          # npm scripts
├── maya/                 # Maya 控制脚本
│   ├── check_scene.py
│   ├── play_scene.py
│   └── send_to_maya.py
├── output/               # 爬取数据（按版本分目录）
│   ├── 2025/
│   ├── 2022/
│   └── 2020/
│       ├── index.json                # 命令分类索引
│       └── maya_commands_python.json # 命令详情（含简介+示例）
└── .trae/skills/         # IDE Skills
    ├── maya-2020-api-doc/
    ├── maya-2025-api-doc/
    └── maya-control-modes/
```

## 使用方式

### 浏览命令文档

```bash
npm run browse
```

打开 `http://localhost:3000`，支持按版本切换、分类筛选、关键词搜索、键盘导航。

### 爬取数据

```bash
npm run cats:2025      # 抓取 2025 分类索引
npm run scrape:2025    # 抓取 2025 命令详情
npm run all:2022       # 一键抓取 2022（分类+详情）

npm run cats:2020
npm run scrape:2020
npm run all:2020
```

### 代理端点

浏览器中的文档链接通过本地代理打开，解决 Autodesk 官网直连访问问题：

```
GET /proxy?url=https://help.autodesk.com/cloudhelp/2025/CHS/Maya-Tech-Docs/CommandsPython/addAttr.html
```

## 数据统计

| 版本 | 命令总数 | 成功爬取 | 有简介 | 有示例 | 404 缺失 |
|------|---------|---------|--------|--------|----------|
| 2025 | 1521    | 1205    | 1199   | 1197   | 316      |
| 2022 | 1503    | 1190    | 1184   | 1182   | 313      |
| 2020 | 1499    | 1186    | 1180   | 1178   | 313      |

数据来源：Autodesk Maya 中文文档 `help.autodesk.com/cloudhelp/{VERSION}/CHS/Maya-Tech-Docs/`
