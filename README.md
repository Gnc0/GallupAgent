# Gallup Skill (Pi)

基于盖洛普 CliftonStrengths 34 个天赋主题的多智能体分析 Pi Skill。

## 工作原理

通过 Supervisor-Worker-Synthesizer 三阶段流程，从多个盖洛普天赋视角深度分析用户问题：

1. **Supervisor** — 分析用户意图，选择 2-5 个最相关的天赋主题
2. **Worker**（并行）— 每个选中的主题从各自视角独立分析
3. **Synthesizer** — 融合所有视角为统一、连贯的最终答案

## 目录结构

```
.pi/
├── agents/
│   ├── gallup-supervisor.md      # 监督者 agent
│   ├── gallup-worker.md          # 工作者 agent
│   └── gallup-synthesizer.md     # 汇总者 agent
└── skills/
    └── gallup/
        ├── SKILL.md              # 技能入口
        └── references/
            └── themes.md         # 34 个天赋主题定义
```

## 使用方式

在项目目录下启动 `pi`，当用户提问需要分析/建议/思考时，skill 自动触发。也可通过 `/skill:gallup` 手动调用。

## 依赖

- [pi](https://github.com/badlogic/pi) coding agent（含 subagent 支持）
- 无 Python 依赖
