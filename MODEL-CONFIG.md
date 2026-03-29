# Gallup 技能 - 模型配置指南

## 概述

Gallup 技能支持使用任何 OpenAI 兼容的 API。你可以配置多个 provider 和模型，并在调用 subagent 时指定使用的模型。

## 配置方式

### 方式一：全局配置（推荐）

编辑 `~/.pi/agent/models.json`，添加你的自定义 provider：

```json
{
  "providers": {
    "my-api": {
      "baseUrl": "https://your-api-endpoint.com/v1",
      "api": "openai-completions",
      "apiKey": "YOUR_API_KEY",
      "models": [
        {
          "id": "my-model",
          "name": "My Model"
        }
      ]
    }
  }
}
```

### 方式二：设置默认模型

编辑 `~/.pi/agent/settings.json`：

```json
{
  "defaultProvider": "my-api",
  "defaultModel": "my-model"
}
```

### 方式三：在调用时指定

在 SKILL.md 中的 subagent 调用时使用 `model` 参数：

```javascript
subagent({
  agent: "gallup-worker",
  model: "my-api/my-model",  // 指定 provider 和模型
  task: "..."
})
```

## 支持的模型格式

| 格式 | 说明 | 示例 |
|------|------|------|
| `provider/model` | 指定 provider 和模型 | `zai/glm-4.7` |
| `model` | 使用默认 provider | `glm-4.7` |
| 省略 | 使用默认配置 | - |

## API Key 配置

支持多种格式：

```json
"apiKey": "sk-actual-key"      // 直接值
"apiKey": "MY_ENV_VAR"         // 环境变量
"apiKey": "!get-api-key.sh"    // Shell 命令
```

## 当前配置

你的 `~/.pi/agent/settings.json` 配置：

```json
{
  "defaultProvider": "zai",
  "defaultModel": "glm-4.7"
}
```

这意味着如果不指定 `model` 参数，subagent 将使用 `zai/glm-4.7`。

## 切换模型示例

### 使用更快的模型

```javascript
subagent({
  agent: "gallup-worker",
  model: "zai/glm-5-turbo",  // 更快的模型
  task: "..."
})
```

### 使用其他 provider

```javascript
subagent({
  agent: "gallup-worker",
  model: "openai/gpt-4",  // OpenAI GPT-4
  task: "..."
})
```

### Worker 和 Synthesizer 使用不同模型

```javascript
// Worker 使用快速模型
subagent({
  agent: "gallup-worker",
  model: "zai/glm-5-turbo",
  task: "..."
})

// Synthesizer 使用高质量模型
subagent({
  agent: "gallup-synthesizer",
  model: "zai/glm-4.7",
  task: "..."
})
```

## 测试配置

运行测试验证配置是否正确：

```bash
# 测试默认模型
pi "使用 gallup 技能分析：我最近总是拖延"

# 测试指定模型
pi "使用 gallup 技能分析：我想要提升工作效率" --model zai/glm-4.7
```

## 常见问题

### Q: 如何添加新的 API provider？

A: 编辑 `~/.pi/agent/models.json`，在 `providers` 中添加新条目。

### Q: API Key 支持环境变量吗？

A: 支持。使用 `"apiKey": "MY_ENV_VAR"` 格式。

### Q: 可以临时切换模型吗？

A: 可以。在 SKILL.md 的 subagent 调用时添加 `model` 参数。

### Q: 模型配置会影响其他技能吗？

A: 不会。每个技能可以独立指定使用的模型。

## 相关文件

- `~/.pi/agent/models.json` - 全局模型配置
- `~/.pi/agent/settings.json` - 默认设置
- `.pi/skills/gallup/SKILL.md` - 技能定义
- `.pi/model-config.example.json` - 配置示例
