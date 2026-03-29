---
name: gallup
description: 基于盖洛普34个天赋主题的多智能体分析。当用户需要从多元视角分析问题、寻求建议、解决困惑或深度思考时使用此技能。
---

# Gallup 多元天赋分析

基于盖洛普 CliftonStrengths 的 34 个天赋主题，从多个天赋视角深度分析用户问题，最后融合为统一答案。

## 快速判断

先判断用户输入是否适合分析：
- ✅ 适合：寻求帮助、分析、建议、解决困惑、职业选择、人际关系等
- ❌ 不适合：打招呼、客观知识问答、角色扮演、内容创作、代码编写等

如果**不适合**，直接正常回复用户，不要启动分析流程。

## 渐进式分析流程（适合时执行）

通过脚本 `extract-themes.js` 按需查询主题信息，**禁止一次性读取所有主题数据**。脚本路径：`<skill_dir>/extract-themes.js`

脚本支持三种查询模式（自动根据参数类型判断）：

| 命令 | 作用 |
|------|------|
| `node extract-themes.js` | 列出4个领域及概述 |
| `node extract-themes.js <域名>` | 列出该领域下所有主题名+描述 |
| `node extract-themes.js <主题英文名> ...` | 提取指定主题的完整内容（`===SEPARATOR===` 分隔） |

### 第一步：浏览领域

```bash
node "<skill_dir>/extract-themes.js"
```

根据用户问题，从4个领域中选出 2-5 个相关领域（确保跨领域多元化）。

### 第二步：浏览选中领域内的主题

对每个选中领域，分别运行：

```bash
node "<skill_dir>/extract-themes.js" <域名>
```

从每个领域中挑选 1 个最匹配用户问题的主题，共 2-5 个。

### 第三步：提取主题内容

将所有选中的主题名一次性传入：

```bash
node "<skill_dir>/extract-themes.js" Theme1 Theme2 Theme3
```

**将输出直接拼入 subagent 的 task，禁止让 worker 自行读取任何文件。**

### 第四步：准备 Session 目录

创建一个唯一的 session 目录用于存储本次分析的所有 worker 结果：

```bash
mkdir -p "<skill_dir>/../sessions/gallup-analysis/$(date +%Y%m%d-%H%M%S)"
```

记录 `session_dir` 路径，格式如：`sessions/gallup-analysis/20260329-213000/`

### 第五步：并行工作者分析

使用 `subagent` 工具，**PARALLEL** 模式调用 `gallup-worker`。

对每个选中的主题，创建一个独立的任务：

```
subagent({
  agent: "gallup-worker",
  cwd: "<skill_dir>/../sessions/gallup-analysis/<timestamp>/",
  task: "主题名称：{ThemeName}

{脚本输出的该主题完整内容}

用户的问题：{用户原始问题}

**重要**：请将你的分析结果保存到文件 `<session_dir>/{ThemeName}.yaml`，格式如下：

```
theme: {主题英文名}
theme_cn: {主题中文名}
domain: {所属领域}
analysis: |
  {你的分析结果内容}
```

使用 write 工具保存文件：
- path: 使用完整路径 `<session_dir>/{ThemeName}.yaml`
- content: YAML 格式的分析结果

请从你的天赋视角，深度分析这个问题，并按上述格式保存结果。"
})
```

### 第六步：汇总结果

使用 `subagent` 工具，SINGLE 模式调用 `gallup-synthesizer`：

```
subagent({
  agent: "gallup-synthesizer",
  cwd: "<skill_dir>/../sessions/gallup-analysis/<timestamp>/",
  task: "用户问题：{用户原始问题}

选择的分析视角：{themes列表}

Session 目录：{session_dir}

**任务**：
1. 使用 ls 或 bash 命令列出 session 目录中的所有 .yaml 文件
2. 使用 read 工具逐个读取这些 YAML 文件
3. 从每个文件中提取 theme 和 analysis 字段
4. 整合所有视角的分析结果，给出一个统一、连贯、有价值的最终答案
5. **将最终答案保存为 synthesis.yaml**，格式：

```yaml
question: {用户原始问题}
themes:
  - {主题1}
  - {主题2}
  - {主题3}
answer: |
  {最终答案内容}
```

请开始分析。"
})
```

### 第七步：呈现结果

将 synthesizer 的最终答案直接呈现给用户。

**Session 目录内容**：
```
sessions/gallup-analysis/{timestamp}/
├── {Theme1}.yaml       # worker 1 的分析
├── {Theme2}.yaml       # worker 2 的分析
├── {Theme3}.yaml       # worker 3 的分析
└── synthesis.yaml      # synthesizer 的最终答案
```

---

## 辅助脚本说明

### extract-themes.js

位置：`<skill_dir>/extract-themes.js`

该脚本从 `references/themes.yaml` 中提取盖洛普主题信息，支持三种查询模式。
