#!/usr/bin/env node

/**
 * 测试不同模型配置的脚本
 *
 * 使用方式：
 * node test-model-config.js
 */

const models = [
  { name: '默认模型', model: null },
  { name: 'GLM-4.7', model: 'zai/glm-4.7' },
  { name: 'GLM-5-Turbo', model: 'zai/glm-5-turbo' },
];

console.log('🧪 Gallup 技能 - 模型配置测试\n');
console.log('当前配置：');
console.log('  默认 Provider: zai');
console.log('  默认 Model: glm-4.7');
console.log('  API 端点: https://open.bigmodel.cn/api/coding/paas/v4\n');

console.log('测试场景：\n');
models.forEach((m, i) => {
  console.log(`${i + 1}. ${m.name}`);
  if (m.model) {
    console.log(`   subagent({ agent: "gallup-worker", model: "${m.model}", task: "..." })`);
  } else {
    console.log(`   subagent({ agent: "gallup-worker", task: "..." })`);
  }
  console.log('');
});

console.log('建议：');
console.log('  - Worker 使用快速模型：zai/glm-5-turbo');
console.log('  - Synthesizer 使用高质量模型：zai/glm-4.7');
console.log('  - 根据需求在 SKILL.md 中调整 model 参数\n');

console.log('查看完整配置：');
console.log('  cat ~/.pi/agent/models.json');
console.log('  cat ~/.pi/agent/settings.json\n');

console.log('文档：');
console.log('  查看 MODEL-CONFIG.md 了解详细配置指南');
