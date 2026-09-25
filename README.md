# AI 代码审查助手（AI Code Review Assistant）

基于大语言模型的智能代码审查工具：粘贴代码 → AI 从**命名规范、逻辑错误、性能问题、安全隐患**四个维度分析 → 以「错误 / 警告 / 建议」三级分类展示审查结果与修改建议，支持注册登录、历史记录回看与审查结果分享。

## 功能特性

- **智能代码审查**：对接 DeepSeek 大模型，输出结构化审查结果，按「错误 / 警告 / 建议」三级分类渲染，支持点击查看问题详情与修改建议
- **在线代码编辑器**：集成 Monaco Editor（VS Code 同款内核），支持 JavaScript / Python / Java 等 14 种语言语法高亮
- **账号系统**：注册 / 登录 / 鉴权中间件，审查记录按用户隔离
- **历史记录**：每次审查自动存档，支持列表回看与详情页复查
- **语言自动识别**：根据粘贴内容自动判断编程语言，匹配对应提示词模板
- **结果分享**：审查结果可生成 8 位随机分享码（如 `/share/aB3xY9zK`），**访客无需登录即可只读查看**；分享者可随时取消分享，撤销后链接立即失效

## 实现亮点与技术难点

### 1. AI 行号校准 —— 程序校准兜底，不信模型的确定性输出

大模型擅长"找问题"却做不好"数行号"（概率模型天生干不了确定性任务，实测 DeepSeek-V3 行号也会系统性偏 1）。因此本项目对 AI 审查结果做**程序化后处理校准**：

| 手段 | 解决的问题 |
|------|-----------|
| 指纹重定位：不用 AI 报的 `line`，改拿 AI 同回的 `original_code` 片段去源码逐行搜索真实行号 | AI 行号漂移 |
| 三级容错匹配：完全相等 → 互相包含 → 去空白引号后比较 | AI 会悄悄"清洗"片段（增减空格、补删引号） |
| 占用集合 `used_lines` 错开候选行 | 重复代码行让多个问题挤到同一行 |
| 结合 `fixed_code` 反查真正改动行、排除纯括号上下文 | 无辜大括号被当问题行 |
| 语法关键词表强制升级为 error | 缺分号等硬错误被模型判成 warning |

架构思想：**让 AI 干它擅长的（读懂代码、发现问题），让程序干该干的（计数、定位、分级）**。工业界同思路用 AST 解析，本项目用"强模型 + 后处理校准"实现。

### 2. 双重鉴权 —— 页面与接口两道防线互不替代

- **前端**：Vue Router 全局前置守卫拦截未登录页面访问并重定向登录页（管"能不能**看到**页面"）
- **后端**：统一登录中间件校验 session，无登录态直接 401（管"能不能**调**接口"）——绕开前端直接请求接口同样被拦

### 3. 数据隔离与防越权（IDOR）

- 登录态存**服务端 session**，用户 id 不由前端传递，请求处理始终以 session 身份为准，从根上防篡改越权
- 主键用 UUID 而非自增 id，防按 id 顺序遍历他人数据
- 路由守卫首访调 `/api/auth/me` 校准登录态；Axios 统一拦截 401 自动跳登录

### 4. 免登录分享 —— 分享码设计

- 审查结果生成 **8 位密码学安全随机分享码**，访客凭码只读查看、无需注册
- 分享**幂等**（重复创建返回原码）、可随时撤销、撤销后链接立即失效
- 查询 JOIN 分享者用户名，访客可知来源

### 5. 模型选型决策链

从硅基流动免费小模型实测（能力不足）→ 换 DeepSeek-V3（解决"洗代码/判级不准"）→ 发现行号偏差是模型通病 → 最终定型"强模型找问题 + 程序精确校准"。**不无脑调 API，先摸清模型能力边界再设计架构**。

## 技术栈

| 端 | 技术 |
|---|---|
| 前端 | Vue3（组合式 API）· Vite · Vue Router · Pinia · Element Plus · Monaco Editor · Axios |
| 后端 | Python Flask（蓝图分层）· SQLite · 自研 .env 配置加载 |
| AI | DeepSeek Chat API · 提示词模板独立管理 |

## 项目结构

```
├── frontend/                 # 前端（Vue3 + Vite）
│   └── src/
│       ├── views/            # 页面：登录 / 注册 / 审查主页 / 历史列表 / 历史详情 / 分享页
│       ├── components/       # 编辑器面板 · 结果面板 · 分享弹窗
│       ├── api/              # Axios 封装（拦截器统一处理）
│       ├── stores/           # Pinia 状态管理
│       └── router/           # 路由与导航守卫（含分享页白名单）
└── backend/                  # 后端（Flask）
    ├── app.py                # 应用工厂 + 蓝图注册
    ├── config.py             # 环境变量加载与配置
    ├── routes/               # auth · review · history · language · share 五组接口
    ├── middleware/           # 登录鉴权中间件
    ├── services/             # 审查服务 · 语言检测
    ├── prompts/              # 大模型提示词模板
    └── database/             # SQLite 初始化与访问（含 shares 表）
```

## 快速开始

### 1. 后端

```bash
cd backend
pip install -r requirements.txt

# 配置环境变量：复制 .env.example 为 .env，填入你自己的 API Key
# Windows:
copy .env.example .env

python app.py
# 后端运行在 http://localhost:5002
```

`.env` 需要包含以下字段（参考 `.env.example`，此文件不会被提交）：

```
LLM_API_KEY=你的DeepSeek_API_Key
LLM_API_BASE=https://api.deepseek.com/v1
LLM_CHAT_MODEL=deepseek-chat
SECRET_KEY=任意随机字符串
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
# 打开终端提示的地址（默认 http://localhost:5175）
```

## 安全说明

- 所有密钥均通过环境变量注入，仓库中不含任何真实 API Key
- `backend/.env` 与数据库文件已通过 `.gitignore` 排除
- 仅供学习交流使用
