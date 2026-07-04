# Maya Command Documentation

Maya Python 命令文档工具集，包含三个部分：**Trae IDE Skills**、**文档爬虫** 和 **Maya 控制脚本**。

支持 Maya 2020 / 2022 / 2025 三个版本。

---

## 项目结构

```
maya_doc/
├── browse.html                # 命令浏览器 UI（数据浏览，独立于爬虫）
├── docs-crawler/              # 文档爬虫
│   ├── scraper.js             # 命令详情爬虫
│   ├── scrape_cats.js         # 分类索引爬虫
│   └── server.js              # 本地浏览服务器（含代理）
├── tools/                     # Skill 配套工具（Maya 外部控制）
│   ├── check_scene.py         # 场景状态检查
│   ├── play_scene.py          # 场景播放控制
│   └── send_to_maya.py        # 脚本发送工具
├── maya-scripts/              # 用户产出的 Maya 脚本（可空）
├── .trae/skills/              # Trae IDE Skills
│   ├── maya-api-doc/          # 总览 Skill（数据结构说明）
│   ├── maya-2020-api-doc/     # Maya 2020 API 文档 Skill
│   ├── maya-2022-api-doc/     # Maya 2022 API 文档 Skill
│   ├── maya-2025-api-doc/     # Maya 2025 API 文档 Skill
│   └── maya-control-modes/    # Maya 外部控制方式 Skill
├── output/                    # 爬取数据（按版本分目录）
│   ├── 2025/
│   │   ├── index.json                    # 命令分类索引
│   │   └── maya_commands_python.json     # 命令详情（含简介+示例）
│   ├── 2022/
│   └── 2020/
├── package.json               # 项目根 npm 配置
└── .gitignore
```

---

## 第一部分：Trae IDE Skills

用于给 Trae IDE（或其他兼容 IDE）的 AI 提供 Maya API 文档问答能力。

### Skill 列表

| Skill 名称 | 说明 |
|-----------|------|
| **maya-api-doc** | 总览 Skill，描述数据结构和查询方法，不包含具体命令数据 |
| **maya-2020-api-doc** | Maya 2020 API 文档（1499 条命令） |
| **maya-2022-api-doc** | Maya 2022 API 文档（1503 条命令） |
| **maya-2025-api-doc** | Maya 2025 API 文档（1521 条命令） |
| **maya-control-modes** | 两种外部控制 Maya 的方式（Standalone + Command Port） |

### 安装 Skill

> 以下操作面向 AI，由 AI 自动完成。

需要读取 Skill 配置文件来注册技能。路径为：

- [maya-api-doc](file:///.trae/skills/maya-api-doc/SKILL.md) — 总览 Skill，应先读取
- [maya-2020-api-doc](file:///.trae/skills/maya-2020-api-doc/SKILL.md)
- [maya-2022-api-doc](file:///.trae/skills/maya-2022-api-doc/SKILL.md)
- [maya-2025-api-doc](file:///.trae/skills/maya-2025-api-doc/SKILL.md)
- [maya-control-modes](file:///.trae/skills/maya-control-modes/SKILL.md)

每个 Skill 的 `SKILL.md` 包含了：
- 功能描述与适用场景
- 数据文件的 JSON 结构说明
- 查询数据的最佳实践（使用 Grep 搜索而非一次性读取整个文件）
- 使用示例

数据文件位于各 Skill 的 `data/` 目录下：
- `index.json`：命令名 → 分类/子分类/是否为 MEL 脚本 的映射
- `maya_commands_python.json`：完整命令文档（描述 + Python 示例）

### 原理

当 AI 需要回答 Maya 命令相关问题（如 *"cmds.addAttr 的参数是什么？"*）时，通过 Grep 在对应的 JSON 数据文件中搜索命令名称，获取其描述和示例代码，从而给出精确的回答。

---

## 第二部分：文档爬虫 (Documentation Crawler)

从 Autodesk 官网爬取 Maya Python 命令文档。

### 安装依赖

```bash
npm install
```

### 爬取数据

```bash
# 爬取分类索引
npm run cats:2025      # Maya 2025
npm run cats:2022      # Maya 2022
npm run cats:2020      # Maya 2020

# 爬取命令详情
npm run scrape:2025    # Maya 2025
npm run scrape:2022    # Maya 2022
npm run scrape:2020    # Maya 2020

# 一键完成（分类 + 详情）
npm run all:2025
npm run all:2022
npm run all:2020
```

爬取结果保存在 `output/{VERSION}/` 目录下：
- `index.json` — 命令分类索引
- `maya_commands_python.json` — 完整命令文档

### 浏览文档

启动本地浏览器，可以按版本切换、分类筛选、关键词搜索：

```bash
npm run browse
```

打开 `http://localhost:3000`

### 代理端点

浏览器中的官方文档链接通过本地代理打开，解决 Autodesk 官网直连访问问题：

```
GET /proxy?url=https://help.autodesk.com/cloudhelp/2025/CHS/Maya-Tech-Docs/CommandsPython/addAttr.html
```

### 数据统计

| 版本 | 命令总数 | 成功爬取 | 有简介 | 有示例 | 404 缺失 |
|------|---------|---------|--------|--------|----------|
| 2025 | 1521    | 1205    | 1199   | 1197   | 316      |
| 2022 | 1503    | 1190    | 1184   | 1182   | 313      |
| 2020 | 1499    | 1186    | 1180   | 1178   | 313      |

数据来源：Autodesk Maya 中文文档 `help.autodesk.com/cloudhelp/{VERSION}/CHS/Maya-Tech-Docs/`

---

## 第三部分：Maya 产出脚本 (maya-scripts)

用户使用 Skill 工具产出的 Maya 脚本目录，现阶段可以为空。

产出后的脚本可直接放入此目录管理。

---

## 配套工具 (tools)

Skill 配套的 Maya 外部控制工具，通过 Maya 的 Command Port（TCP 6000 端口）从外部 Python 控制运行中的 Maya GUI 实例。

### 使用方法

1. 在 Maya 中开启 Command Port：

```python
import maya.cmds as cmds
cmds.commandPort(name=":6000", sourceType="python")
```

2. 运行脚本：

```bash
python tools/check_scene.py     # 检查场景状态
python tools/play_scene.py      # 播放场景
python tools/send_to_maya.py    # 发送脚本到 Maya```

### 脚本说明

| 脚本 | 功能 |
|------|------|
| [check_scene.py](file:///tools/check_scene.py) | 连接测试 + 场景状态检查（Mesh 数量、对象存在性验证） |
| [play_scene.py](file:///tools/play_scene.py) | 将时间设为第 1 帧并播放动画 |
| [send_to_maya.py](file:///tools/send_to_maya.py) | 将外部 `.py` 文件发送到 Maya 中执行 |

### 适用场景

- **Standalone 模式**：通过 `mayapy.exe` 在无 GUI 环境下批处理，适合自动化/CI
- **Command Port 模式**：连接正在运行的 Maya GUI 实例实时发送命令，适合交互式操作
