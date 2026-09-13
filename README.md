# AI 代码审查助手（AI Code Review Assistant）

基于大语言模型的智能代码审查工具：粘贴代码 → AI 从**命名规范、逻辑错误、性能问题、安全隐患**四个维度分析 → 以「错误 / 警告 / 建议」三级分类展示审查结果与修改建议，支持注册登录与历史记录回看。

## 功能特性

- **智能代码审查**：对接 DeepSeek 大模型，输出结构化审查结果，按「错误 / 警告 / 建议」三级分类渲染，支持点击查看问题详情与修改建议
- **在线代码编辑器**：集成 Monaco Editor（VS Code 同款内核），支持 JavaScript / Python / Java 等 14 种语言语法高亮
- **账号系统**：注册 / 登录 / 鉴权中间件，审查记录按用户隔离
- **历史记录**：每次审查自动存档，支持列表回看与详情页复查
- **语言自动识别**：根据粘贴内容自动判断编程语言，匹配对应提示词模板

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
│       ├── views/            # 页面：登录 / 注册 / 审查主页 / 历史列表 / 历史详情
│       ├── components/       # 编辑器面板 · 结果面板
│       ├── api/              # Axios 封装（拦截器统一处理）
│       ├── stores/           # Pinia 状态管理
│       └── router/           # 路由与导航守卫
└── backend/                  # 后端（Flask）
    ├── app.py                # 应用工厂 + 蓝图注册
    ├── config.py             # 环境变量加载与配置
    ├── routes/               # auth · review · history · language 四组接口
    ├── middleware/           # 登录鉴权中间件
    ├── services/             # 审查服务 · 语言检测
    ├── prompts/              # 大模型提示词模板
    └── database/             # SQLite 初始化与访问
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
