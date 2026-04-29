#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const SKILLS = [
  // 14 analyst agents
  'agent-axel', 'agent-blaine', 'agent-cass', 'agent-frank',
  'agent-hugo', 'agent-jaya', 'agent-marco', 'agent-mr-a',
  'agent-nadia', 'agent-nina', 'agent-rex', 'agent-sage',
  'agent-tara', 'agent-vera',
  // Orchestrators + solo skills
  'alpha', 'analyze', 'chart', 'edge-pipeline', 'macro',
  'market-top', 'news', 'options-advisor', 'position-size',
  'screen', 'social', 'valuation',
  // The Money module
  'tm-agent-quant', 'tm-dashboard', 'tm-deploy', 'tm-morning',
  'tm-regime', 'tm-review', 'tm-setup', 'tm-synthesis',
];

const DIVIDER = '─'.repeat(60);

const srcBase = path.join(__dirname, '..', '.claude', 'skills');
const targetBase = path.join(os.homedir(), '.claude', 'skills');

console.log('\nTrading Desk — Claude Code Skills Installer');
console.log(DIVIDER);
console.log(`Target: ${targetBase}\n`);

fs.mkdirSync(targetBase, { recursive: true });

let installed = 0;
let failed = 0;

for (const skill of SKILLS) {
  const src = path.join(srcBase, skill);
  const dest = path.join(targetBase, skill);

  if (!fs.existsSync(src)) {
    console.log(`  skip  ${skill}`);
    continue;
  }

  try {
    fs.cpSync(src, dest, { recursive: true });
    console.log(`  ok    ${skill}`);
    installed++;
  } catch (err) {
    console.error(`  fail  ${skill}: ${err.message}`);
    failed++;
  }
}

console.log(`\nInstalled: ${installed}  Failed: ${failed}`);
console.log(DIVIDER);

console.log(`
NEXT STEPS
${DIVIDER}

1. Configure MCP servers in your project .mcp.json
   See: https://github.com/ChouBokYann/trading-desk#mcp-servers

   Minimum: yahoo-finance, financekit, opennews

2. Add the command block to your project CLAUDE.md
   See: https://github.com/ChouBokYann/trading-desk#claudemd-template

3. Open your project in Claude Code and try:
   /news AAPL
   /analyze TSLA
   /tm-morning
${DIVIDER}
`);
