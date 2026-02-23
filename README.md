# GallupAgent

基于盖洛普 CliftonStrengths（34个天赋主题）的多智能体 AI 助手，通过智能协作提供多视角分析。
在评测kimi2.5、deepseekV3.2、Grok4.1、gemini3 pro、glm-4.7、minimax的时候发现，deepseek的数字泔水非常严重，经常性啰嗦+废话，而且文风极为浮夸；反之，kimi2.5不仅能够实现意图对齐，并且能够帮助用户优化问题，并提供结构化的洞察。
使用了一些顶会的提示词增强技术后，发现llm产出质量显著提升，于是乎开始琢磨能不能通过智能体编排丰富llm的推理轨迹，最终采用了gallup理论，使用34个天赋主题作为llm的软约束，并简单地用minimax agent搓了个agent demo，能够显著缓解单次回复的数字泔水现象。

## 简介

GallupAgent 是一个**单次交互式** AI 助手，基于盖洛普的 34 个天赋主题（涵盖 4 大领域）提供多视角分析。系统采用监督者-工作者（Supervisor-Worker）架构，监督者智能分析用户意图并选择 2-5 个相关主题，协调多个工作智能体从各自视角提供分析，最终综合成统一的回答。

### 架构图

```
用户输入 → 监督者智能体 → 工作智能体（2-5个主题）→ 综合分析 → 回答
                  ↓
            意图分析与主题选择
```

## 功能特性

- **多智能体协作**：每次问题协调 2-5 个不同主题的智能体共同分析
- **智能主题选择**：监督者智能体分析意图，从不同领域选择最相关的主题
- **响应综合**：将多个视角融合成统一、连贯的回答
- **对话记录**：自动保存所有对话到 YAML 文件，便于回顾
- **交互式命令行**：友好的命令行界面，提供便捷操作命令

## 盖洛普 4 大领域与 34 主题

| 领域 | 主题 |
|------|------|
| **执行力** | 成就、统筹、信仰、公平、审慎、纪律、专注、责任、排难 |
| **影响力** | 行动、统率、沟通、竞争、完美、自信、追求、取悦 |
| **关系建立** | 适应、关联、发展、共情、和谐、包容、个别、积极、交往 |
| **战略思维** | 分析、回顾、未来、理念、搜集、思维、学习、战略 |

## 环境要求

- Python 3.9+
- 以下 Python 包：
  - `langchain-openai`
  - `langchain-core`
  - `langgraph`
  - `python-dotenv`
  - `pyyaml`

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/Gnc0/GallupAgent.git
cd GallupAgent
```

2. 安装依赖：
```bash
pip install langchain-openai langchain-core langgraph python-dotenv pyyaml
```

3. 配置环境变量：
```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 API 密钥。

## 配置

### 使用 DeepSeek（默认）

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

### 使用 LM Studio（本地）

```env
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=lm-studio
LLM_MODEL=qwen2.5-7b-instruct
```

切换 LLM 提供商，修改 [config.py](config.py) 中的 `Config.CURRENT_LLM`：
```python
CURRENT_LLM: str = "deepseek"  # 或 "lmstudio"
```

## 使用方法

### 启动应用

```bash
python main.py
```

### 交互命令

启动后可使用以下命令：

- 输入任何问题以获取多视角分析
- `help` - 显示帮助信息
- `themes` - 列出所有 34 个盖洛普主题
- `domains` - 按领域显示主题
- `exit` - 退出应用

### 示例对话

```
==================================================
  Gallup Agent - 盖洛普智能体助手
==================================================
输入 'help' 查看帮助，输入 'exit' 退出

> 我在职业选择上很纠结

[协作模式] 调用 3 个主题: Strategic, Learner, Self-Assurance

【分析视角】
基于您的问题，我选择了以下主题：
- Strategic: 帮助您从长远角度规划职业路径
- Learner: 探索您对新知识和技能的吸收能力
- Self-Assurance: 评估您的决策信心和自我认知

  ✓ Strategic 完成
  ✓ Learner 完成
  ✓ Self-Assurance 完成

[综合回答]
（此处为综合后的完整回答...）

[记录已保存] conversations/conversation_20260223_205633.yaml
```

## 项目结构

```
GallupAgent/
├── main.py              # 主入口，交互式命令行界面
├── config.py            # LLM 配置（DeepSeek/LM Studio）
├── logger.py            # 对话记录保存到 YAML
├── quick_test.py        # 快速 API 测试脚本
├── .env                 # 环境变量（API 密钥）
├── .env.example         # 环境变量模板
├── .gitignore
├── .vscode/             # VS Code 调试配置
├── agent/
│   ├── supervisor.py    # 主智能体，负责意图分析
│   ├── worker.py        # 子智能体，各盖洛普主题专家
│   ├── graph.py         # LangGraph 工作流定义
│   └── __init__.py
├── data/
│   ├── themes.py        # 34 个盖洛普主题定义
│   └── __init__.py
├── conversations/       # YAML 对话记录
└── utils/               # （预留，未来工具）
```

## 核心组件

### 监督者智能体 ([agent/supervisor.py](agent/supervisor.py))
分析用户意图并选择相关的盖洛普主题。输出 JSON 控制指令，包含任务、推理和目标智能体。

### 工作者智能体 ([agent/worker.py](agent/worker.py))
从特定盖洛普主题视角执行分析，使用深度对话协议识别用户潜在问题。

### 主应用 ([main.py](main.py))
编排多智能体工作流程并综合响应。

## 对话记录

所有对话自动保存到 `conversations/` 目录，文件名带时间戳：
```
conversations/conversation_YYYYMMDD_HHMMSS.yaml
```

每条记录包含：
- 用户输入
- AI 回答
- 选择的主题
- 主题推理
- 各主题分析结果
- 元数据（任务、主题数量）

## 开发

### 快速测试

测试 API 配置：
```bash
python quick_test.py
```

### VS Code 调试

项目包含 VS Code 调试配置。
