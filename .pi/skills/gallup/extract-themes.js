#!/usr/bin/env node
/**
 * 渐进式查询盖洛普天赋主题，按需暴露信息，避免一次性展示全部内容。
 *
 * 用法：
 *   node extract-themes.js                     → 列出4个领域及其概述
 *   node extract-themes.js 执行力              → 列出该领域下的主题名+描述
 *   node extract-themes.js Strategic 审慎      → 提取指定主题的完整内容
 *
 * 脚本自动判断参数类型（域名/主题名），无需指定模式。
 */

const fs = require('fs');
const path = require('path');

const yamlPath = path.join(__dirname, 'references', 'themes.yaml');
const raw = fs.readFileSync(yamlPath, 'utf-8');

// ── 极简 YAML 解析 ──
function parseYaml(text) {
  const domains = {};        // { 执行力: { desc, themes: [...] } }
  const themeLookup = {};    // { Achiever: {...}, 成就: {...} }
  const domainNames = [];

  let currentDomain = null;
  let inDomains = false;
  let inThemes = false;
  let currentTheme = null;

  for (const line of text.split('\n')) {
    // 顶层 keys
    const topKey = line.match(/^(\S+):\s*$/);
    if (topKey && !line.startsWith(' ')) {
      if (topKey[1] === 'domains') inDomains = true, inThemes = false;
      if (topKey[1] === 'themes') inThemes = true, inDomains = false;
      continue;
    }

    if (inDomains) {
      // 领域名
      const dm = line.match(/^  (\S+):\s*$/);
      if (dm) { currentDomain = dm[1]; domains[currentDomain] = { desc: '', themes: [] }; domainNames.push(currentDomain); continue; }
      // 领域描述
      const dd = line.match(/^    desc:\s+(.+)/);
      if (dd && currentDomain) { domains[currentDomain].desc = dd[1].trim(); continue; }
    }

    if (inThemes) {
      // 领域名
      const dm = line.match(/^  (\S+):\s*$/);
      if (dm) { currentDomain = dm[1]; continue; }
      // 新主题
      const tm = line.match(/^    - en:\s+(\S+)/);
      if (tm) {
        currentTheme = { en: tm[1], domain: currentDomain };
        domains[currentDomain].themes.push(currentTheme);
        themeLookup[currentTheme.en] = currentTheme;
        continue;
      }
      // 主题字段
      const fm = line.match(/^      (zh|desc|traits|angle):\s+(.+)/);
      if (fm && currentTheme) { currentTheme[fm[1]] = fm[2].trim(); themeLookup[currentTheme.zh] = currentTheme; continue; }
    }
  }

  return { domains, domainNames, themeLookup };
}

const { domains, domainNames, themeLookup } = parseYaml(raw);
const args = process.argv.slice(2);

// ── 层级1：无参数 → 领域概览 ──
if (args.length === 0) {
  for (const name of domainNames) {
    console.log(`${name} — ${domains[name].desc}`);
  }
  process.exit(0);
}

// ── 层级2：参数是域名 → 主题摘要 ──
const matchedDomains = args.filter(a => domains[a]);
if (matchedDomains.length > 0) {
  for (const name of matchedDomains) {
    console.log(`【${name}】`);
    for (const t of domains[name].themes) {
      console.log(`  ${t.en}（${t.zh}）：${t.desc}`);
    }
    console.log();
  }
}

// ── 层级3：参数是主题名 → 完整内容 ──
const matchedThemes = args.filter(a => themeLookup[a]);
if (matchedThemes.length > 0) {
  const seen = new Set();
  const results = [];
  for (const name of matchedThemes) {
    const t = themeLookup[name];
    if (seen.has(t.en)) continue;
    seen.add(t.en);
    results.push(
      `你的天赋主题：${t.en}（${t.zh}）\n描述：${t.desc}\n核心特质：${t.traits}\n分析角度：${t.angle}`
    );
  }
  if (results.length > 0) console.log(results.join('\n\n===SEPARATOR===\n\n'));
}

// 没有任何匹配时报错
if (matchedDomains.length === 0 && matchedThemes.length === 0) {
  console.error(`未找到匹配: ${args.join(', ')}\n运行无参数可查看可用领域`);
  process.exit(1);
}
