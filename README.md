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

## 模型配置

Gallup 技能支持任何 OpenAI 兼容的 API。你可以：

1. **配置自定义 API** - 编辑 `~/.pi/agent/models.json` 添加你的 provider
2. **设置默认模型** - 在 `~/.pi/agent/settings.json` 中配置
3. **调用时指定模型** - 在 SKILL.md 中使用 `model` 参数

详细配置指南请参考 [MODEL-CONFIG.md](MODEL-CONFIG.md)

### 当前配置

- **默认 Provider**: `zai`
- **默认 Model**: `glm-4.7`
- **API 端点**: `https://open.bigmodel.cn/api/coding/paas/v4`

## 特性

- ✅ 多视角分析 - 从 2-5 个盖洛普天赋主题视角深度分析
- ✅ Session 持久化 - 所有分析结果保存为 YAML 文件
- ✅ 灵活配置 - 支持任何 OpenAI 兼容的 API
- ✅ 并行处理 - Worker agents 并行分析，提升效率
- ✅ 无 Python 依赖 - 纯 Pi 技能实现

## 依赖

- [pi](https://github.com/badlogic/pi) coding agent（含 subagent 支持）
- 无 Python 依赖

## Session 数据

每次分析会在 `sessions/gallup-analysis/` 目录保存：

```
sessions/gallup-analysis/{timestamp}/
├── {Theme1}.yaml      # Worker 1 分析
├── {Theme2}.yaml      # Worker 2 分析
├── {Theme3}.yaml      # Worker 3 分析
└── synthesis.yaml     # 最终整合答案
```
