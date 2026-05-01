#!/usr/bin/env node

/**
 * Generates build/dashboard.html — a standalone design-token migration dashboard.
 * Run: node scripts/build-dashboard.js
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TOKENS_DIR = path.join(ROOT, 'tokens');
const BUILD_DIR = path.join(ROOT, 'build');
const TRACKER_PATH = path.join(ROOT, 'migration', 'FIGMA-TOKEN-TRACKER.md');

// ── Token counting ──────────────────────────────────────────────────────────

function countTokensInObject(obj) {
  let count = 0;
  for (const key of Object.keys(obj)) {
    if (key === '$type') count++;
    else if (typeof obj[key] === 'object' && obj[key] !== null) count += countTokensInObject(obj[key]);
  }
  return count;
}

function classifyTier(relativePath) {
  if (relativePath.startsWith('core/')) return 'Core';
  if (relativePath.startsWith('global/')) return 'Global';
  if (relativePath.startsWith('semantic/')) return 'Semantic';
  if (relativePath.startsWith('component/')) return 'Component';
  return 'Other';
}

function collectTokenFiles() {
  const results = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name.endsWith('.json') && !entry.name.startsWith('$')) {
        const relative = path.relative(TOKENS_DIR, full).replace(/\\/g, '/');
        try {
          const data = JSON.parse(fs.readFileSync(full, 'utf8'));
          const tokenCount = countTokensInObject(data);
          if (tokenCount > 0) results.push({ file: relative, tier: classifyTier(relative), count: tokenCount });
        } catch (_) {}
      }
    }
  }
  walk(TOKENS_DIR);
  return results;
}

// ── Tracker parsing ─────────────────────────────────────────────────────────

function parseTracker() {
  if (!fs.existsSync(TRACKER_PATH)) return { priorities: [], components: [] };
  const md = fs.readFileSync(TRACKER_PATH, 'utf8');
  const priorities = [];
  const components = [];
  let currentPriority = null;

  for (const line of md.split('\n')) {
    const prioMatch = line.match(/^## (Priority \d+): (.+)/);
    if (prioMatch) {
      currentPriority = { id: prioMatch[1], name: prioMatch[2], components: [] };
      priorities.push(currentPriority);
      continue;
    }
    const rowMatch = line.match(
      /^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*\[([x~! ])\]\s*\|\s*\[([x~! ])\]\s*\|\s*\[([x~! ])\]\s*\|\s*\[([x~! ])\]\s*\|\s*(.*?)\s*\|$/
    );
    if (rowMatch && currentPriority) {
      const comp = {
        number: parseInt(rowMatch[1], 10),
        name: rowMatch[2].trim(),
        mapped: rowMatch[3] === 'x',
        figmaApplied: rowMatch[4] === 'x',
        verified: rowMatch[5] === 'x',
        storybook: rowMatch[6] === 'x',
        notes: rowMatch[7].trim(),
        priority: currentPriority.id,
        priorityName: currentPriority.name,
      };
      currentPriority.components.push(comp);
      components.push(comp);
    }
  }
  return { priorities, components };
}

// ── Static data ─────────────────────────────────────────────────────────────

const BOUND_COMPONENTS = [
  { name: 'Pill Button', bindings: 756, uniqueTokens: 46, properties: 'fill, borderColor, borderRadius, borderWidth, typography, spacing', status: 'full' },
  { name: 'Button', bindings: 717, uniqueTokens: 70, properties: 'fill, borderColor, borderRadius, borderWidth, typography, spacing', status: 'full' },
  { name: 'Accordion', bindings: 494, uniqueTokens: 23, properties: 'fill, borderColor, typography, spacing', status: 'full' },
  { name: 'Badge', bindings: 297, uniqueTokens: 17, properties: 'fill, borderColor, borderRadius, borderWidth, typography, spacing', status: 'full' },
  { name: 'Alert Box', bindings: 282, uniqueTokens: 36, properties: 'fill, borderColor, borderRadius, borderWidth, typography, spacing', status: 'full' },
  { name: 'Checkbox', bindings: 105, uniqueTokens: 16, properties: 'fill, borderColor, borderRadius, borderWidth', status: 'full' },
  { name: 'Stepper', bindings: 99, uniqueTokens: 16, properties: 'fill, borderColor', status: 'full' },
  { name: 'Radio Button', bindings: 60, uniqueTokens: 16, properties: 'fill, borderColor, borderWidth, typography', status: 'full' },
  { name: 'Side Panel', bindings: 44, uniqueTokens: 7, properties: 'fill, borderRadius, typography, spacing', status: 'full' },
  { name: 'Display Heading', bindings: 36, uniqueTokens: 9, properties: 'fill, typography, textDecorationColor', status: 'full' },
  { name: 'Toggle', bindings: 35, uniqueTokens: 20, properties: 'fill, borderColor', status: 'full' },
  { name: 'Dropdown', bindings: 29, uniqueTokens: 16, properties: 'fill, borderColor, borderRadius, borderWidth, spacing', status: 'full' },
  { name: 'Loading Spinner', bindings: 26, uniqueTokens: 6, properties: 'fill', status: 'full' },
  { name: 'Input Field', bindings: 19, uniqueTokens: 2, properties: 'fill, borderColor', status: 'partial' },
  { name: 'Toast', bindings: 18, uniqueTokens: 9, properties: 'fill, borderRadius, boxShadow, typography, spacing', status: 'full' },
  { name: 'Pagination Button', bindings: 11, uniqueTokens: 9, properties: 'fill, borderColor, borderRadius, borderWidth, typography, spacing', status: 'full' },
  { name: 'Date Picker', bindings: 8, uniqueTokens: 1, properties: 'fill', status: 'partial' },
];

const UNBOUND_COMPONENTS = [
  'Circle Button', 'Countdown Timer', 'Double Range Input',
  'Filter Bar', 'Image', 'Modal', 'Phone Number Field',
  'PopOver', 'Square Button', 'Tooltip',
];

// Tracker aliases — components that appear under a different name in the tracker
const TRACKER_ALIASES = {
  'Toggler BarBlock': 'Filter Bar',
};

const TOKEN_FILE_COMPONENTS = [
  { name: 'Toggle', file: 'component/toggle.json', tokens: 20 },
  { name: 'Stepper', file: 'component/stepper.json', tokens: 22 },
  { name: 'Toast', file: 'component/toast.json', tokens: 9 },
  { name: 'Loading Spinner', file: 'component/loading.json', tokens: 11 },
  { name: 'Popover', file: 'component/popover.json', tokens: 9 },
];

const KNOWN_ISSUES = [
  { severity: 'Critical', title: 'Zero-width Unicode in token names', detail: 'Invisible characters in semantic color-light keys (primary, selected). Will cause binding failures.', impact: 'Tokens fail to resolve in Figma and code output.' },
  { severity: 'Critical', title: 'Spaces in directory names', detail: 'component / spacing / directories have whitespace. Style Dictionary globs break.', impact: 'Build pipeline cannot process mobile/desktop spacing tokens.' },
  { severity: 'High', title: 'Desktop/mobile naming inconsistency', detail: 'Desktop uses camelCase, mobile uses kebab-case for the same tokens.', impact: 'Cannot share references across breakpoints.' },
  { severity: 'High', title: 'Mobile tokens append px to references', detail: 'Mobile token values like "{core.dimension.600}px" produce double units.', impact: 'Broken CSS output for all mobile spacing tokens.' },
  { severity: 'High', title: 'Mobile missing button spacing', detail: 'Mobile spacing set has no button.spacing group.', impact: 'Buttons cannot be fully tokenised for mobile.' },
  { severity: 'Medium', title: 'No dark theme variant', detail: 'Only colorLight.json exists. No dark theme authored yet.', impact: 'Dark mode not supported.' },
  { severity: 'Medium', title: 'Disabled color naming', detail: 'Disabled colors use opaque names (a, b, c) instead of descriptive keys.', impact: 'Low discoverability for designers and developers.' },
];

const RECENT_ACTIVITY = [
  { date: '2026-04-30', item: 'Toggle component tokens created (18 colour tokens, 3 state groups)' },
  { date: '2026-04-30', item: 'Presale semantic colour added (color.interactive.presale)' },
  { date: '2026-04-30', item: 'Toggle Figma bindings applied (12 variants, Token Studio sharedPluginData)' },
  { date: '2026-04-30', item: 'Figma Token Applicator skill updated with 6 workflow rules' },
  { date: '2026-04-21', item: 'Radio Button bindings applied (14 variants, 60 bindings)' },
  { date: '2026-04-18', item: 'Toast component tokens created and bound (2 variants)' },
  { date: '2026-04-15', item: 'Stepper component tokens created' },
  { date: '2026-04-14', item: 'Loading Spinner & Popover component tokens created' },
];

// ── SVG helpers ─────────────────────────────────────────────────────────────

function svgDonut(pct, color, size, strokeWidth, label, sublabel) {
  const r = (size - strokeWidth) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  const cx = size / 2;
  const cy = size / 2;
  return `<div class="donut-wrap">
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#e8e8ed" stroke-width="${strokeWidth}"/>
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${color}" stroke-width="${strokeWidth}"
        stroke-dasharray="${circ}" stroke-dashoffset="${offset}" stroke-linecap="round"
        transform="rotate(-90 ${cx} ${cy})" class="donut-arc"/>
      <text x="${cx}" y="${cy - 4}" text-anchor="middle" fill="${color}" font-size="22" font-weight="700">${label}</text>
      <text x="${cx}" y="${cy + 14}" text-anchor="middle" fill="#949494" font-size="10" font-weight="500">${sublabel}</text>
    </svg>
  </div>`;
}

function svgPieChart(segments, size) {
  const cx = size / 2;
  const cy = size / 2;
  const r = size / 2 - 2;
  const total = segments.reduce((s, seg) => s + seg.value, 0);
  let cumAngle = -90;
  const paths = [];

  for (const seg of segments) {
    const angle = (seg.value / total) * 360;
    const startRad = (cumAngle * Math.PI) / 180;
    const endRad = ((cumAngle + angle) * Math.PI) / 180;
    const largeArc = angle > 180 ? 1 : 0;
    const x1 = cx + r * Math.cos(startRad);
    const y1 = cy + r * Math.sin(startRad);
    const x2 = cx + r * Math.cos(endRad);
    const y2 = cy + r * Math.sin(endRad);

    if (angle >= 359.99) {
      paths.push(`<circle cx="${cx}" cy="${cy}" r="${r}" fill="${seg.color}"/>`);
    } else {
      paths.push(`<path d="M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${largeArc},1 ${x2},${y2} Z" fill="${seg.color}">
        <title>${seg.label}: ${seg.value} (${((seg.value / total) * 100).toFixed(1)}%)</title>
      </path>`);
    }
    cumAngle += angle;
  }

  return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">${paths.join('')}</svg>`;
}

// ── HTML generation ─────────────────────────────────────────────────────────

function generateHtml(tokenFiles, tracker) {
  const totalTokens = tokenFiles.reduce((s, f) => s + f.count, 0);
  const totalFiles = tokenFiles.length;
  const totalComponents = tracker.components.length;
  const appliedComponents = tracker.components.filter((c) => c.figmaApplied).length;
  const mappedComponents = tracker.components.filter((c) => c.mapped).length;
  const verifiedComponents = tracker.components.filter((c) => c.verified).length;

  const tierTotals = {};
  for (const f of tokenFiles) tierTotals[f.tier] = (tierTotals[f.tier] || 0) + f.count;

  const tierOrder = ['Core', 'Global', 'Semantic', 'Component'];
  const tierColors = { Core: '#6366f1', Global: '#8b5cf6', Semantic: '#024dff', Component: '#048851' };
  const severityColors = { Critical: '#EB0000', High: '#e8920d', Medium: '#207de5', Low: '#048851' };
  const severityBg = { Critical: '#fef2f2', High: '#fffbeb', Medium: '#eff6ff', Low: '#ecfdf5' };

  const fullBound = BOUND_COMPONENTS.filter((c) => c.status === 'full').length;
  const partialBound = BOUND_COMPONENTS.filter((c) => c.status === 'partial').length;
  const totalBound = BOUND_COMPONENTS.length;
  const unboundCount = UNBOUND_COMPONENTS.length;
  const mappedPct = totalComponents > 0 ? Math.round((mappedComponents / totalComponents) * 100) : 0;
  const boundPct = totalComponents > 0 ? Math.round((totalBound / totalComponents) * 100) : 0;
  const fullBoundPct = totalComponents > 0 ? Math.round((fullBound / totalComponents) * 100) : 0;
  const verifiedPct = totalComponents > 0 ? Math.round((verifiedComponents / totalComponents) * 100) : 0;
  const totalBindings = BOUND_COMPONENTS.reduce((s, c) => s + c.bindings, 0);

  const now = new Date().toISOString().slice(0, 10);

  const pieSegments = tierOrder
    .filter((t) => tierTotals[t])
    .map((t) => ({ label: t, value: tierTotals[t], color: tierColors[t] }));

  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GDS Design Token Migration — Dashboard</title>
<style>
  :root {
    --neptune: #024dff;
    --neptune-10: rgba(2,77,255,0.1);
    --cosmos: #121212;
    --spotlight: #ffffff;
    --slate: #949494;
    --moonrock: #BFBFBF;
    --diatomite: #EBEBEB;
    --fog: #F8F9FB;
    --success: #048851;
    --success-10: rgba(4,136,81,0.1);
    --error: #EB0000;
    --warning: #FFB932;
    --info: #207de5;
    --magenta: #D0006F;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
    --radius: 12px;
    --radius-sm: 8px;
    --radius-xs: 6px;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif; background: var(--fog); color: var(--cosmos); line-height: 1.5; -webkit-font-smoothing: antialiased; }

  /* ── Header ── */
  .header {
    background: linear-gradient(135deg, var(--cosmos) 0%, #0d1b3e 50%, #0a2463 100%);
    color: var(--spotlight);
    padding: 40px 48px 80px;
    position: relative;
    overflow: hidden;
  }
  .header::after {
    content: '';
    position: absolute;
    top: -60%;
    right: -10%;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(2,77,255,0.15) 0%, transparent 70%);
  }
  .header h1 { font-size: 28px; font-weight: 800; letter-spacing: -0.02em; position: relative; z-index: 1; }
  .header p { font-size: 14px; color: rgba(255,255,255,0.6); margin-top: 4px; position: relative; z-index: 1; }

  .container { max-width: 1200px; margin: 0 auto; padding: 0 40px 60px; }

  /* ── Hero metrics ── */
  .hero-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-top: -56px;
    position: relative;
    z-index: 2;
    margin-bottom: 40px;
  }
  .hero-card {
    background: var(--spotlight);
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: var(--shadow-md);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .hero-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
  .donut-wrap { display: flex; justify-content: center; margin-bottom: 8px; }
  .donut-arc { transition: stroke-dashoffset 1s ease-out; }
  .hero-card .hero-label { font-size: 13px; font-weight: 600; color: var(--slate); text-transform: uppercase; letter-spacing: 0.04em; }

  /* ── Section styling ── */
  .section { margin-bottom: 40px; }
  .section-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 20px; }
  .section-header h2 { font-size: 20px; font-weight: 700; letter-spacing: -0.01em; }
  .section-header .section-line { flex: 1; height: 1px; background: var(--diatomite); }

  /* ── Two-column layout ── */
  .grid-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }

  /* ── Panel (white cards) ── */
  .panel { background: var(--spotlight); border-radius: var(--radius); padding: 28px; box-shadow: var(--shadow-sm); }
  .panel h3 { font-size: 15px; font-weight: 700; margin-bottom: 16px; color: var(--cosmos); }

  /* ── Pie chart + legend ── */
  .pie-layout { display: flex; align-items: center; gap: 32px; }
  .pie-legend { flex: 1; }
  .pie-legend-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--fog); }
  .pie-legend-row:last-child { border-bottom: none; }
  .pie-swatch { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
  .pie-legend-label { flex: 1; font-size: 14px; font-weight: 500; }
  .pie-legend-value { font-size: 14px; font-weight: 700; color: var(--cosmos); }
  .pie-legend-pct { font-size: 12px; color: var(--slate); width: 45px; text-align: right; }

  /* ── Bar chart for files ── */
  .bar-chart { margin-top: 8px; }
  .bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
  .bar-file { width: 200px; font-size: 12px; color: #555; text-align: right; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .bar-track { flex: 1; height: 18px; background: var(--fog); border-radius: 9px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 9px; transition: width 0.6s ease-out; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; }
  .bar-fill span { font-size: 10px; font-weight: 700; color: #fff; }
  .bar-count { width: 35px; font-size: 12px; font-weight: 600; color: var(--cosmos); }

  /* ── Pipeline chart ── */
  .pipeline { display: flex; flex-direction: column; gap: 16px; }
  .pipeline-row { display: flex; align-items: center; gap: 12px; }
  .pipeline-label { width: 140px; font-size: 13px; font-weight: 600; color: var(--cosmos); flex-shrink: 0; }
  .pipeline-track { flex: 1; height: 28px; background: #f0f1f4; border-radius: 14px; overflow: hidden; position: relative; }
  .pipeline-fill { height: 100%; border-radius: 14px; transition: width 0.8s ease-out; display: flex; align-items: center; padding-left: 12px; min-width: 2px; }
  .pipeline-fill span { font-size: 12px; font-weight: 700; color: #fff; white-space: nowrap; }
  .pipeline-val { width: 60px; font-size: 13px; font-weight: 700; text-align: right; flex-shrink: 0; }

  /* ── Priority group chart ── */
  .prio-chart { margin-top: 8px; }
  .prio-group { margin-bottom: 20px; }
  .prio-group-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
  .prio-group-header h4 { font-size: 14px; font-weight: 600; }
  .prio-group-header .prio-count { font-size: 12px; color: var(--slate); }
  .prio-stacked-bar { display: flex; height: 32px; border-radius: 8px; overflow: hidden; background: #f0f1f4; }
  .prio-seg { display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #fff; transition: flex 0.6s ease-out; min-width: 0; }
  .prio-seg-mapped { background: var(--neptune); }
  .prio-seg-applied { background: var(--success); }
  .prio-seg-remaining { background: transparent; }
  .prio-legend-bar { display: flex; gap: 16px; margin-top: 4px; }
  .prio-legend-bar span { font-size: 11px; color: var(--slate); display: flex; align-items: center; gap: 4px; }
  .prio-legend-bar .dot { width: 8px; height: 8px; border-radius: 2px; display: inline-block; }

  /* ── Component grid ── */
  .comp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
  .comp-cell {
    background: var(--fog);
    border-radius: var(--radius-xs);
    padding: 14px 16px;
    text-align: center;
    position: relative;
    border: 1px solid transparent;
    transition: all 0.2s;
  }
  .comp-cell:hover { border-color: var(--diatomite); background: var(--spotlight); }
  .comp-cell .comp-name { font-size: 13px; font-weight: 600; margin-bottom: 6px; }
  .comp-cell .comp-pips { display: flex; gap: 4px; justify-content: center; margin-bottom: 6px; }
  .comp-pip { width: 18px; height: 6px; border-radius: 3px; }
  .pip-done { background: var(--success); }
  .pip-empty { background: var(--diatomite); }
  .comp-cell.is-bound { border-color: var(--success); background: var(--success-10); }
  .comp-cell.is-partial { border-color: var(--warning); background: rgba(255,185,50,0.08); }
  .comp-attached { display: flex; align-items: center; justify-content: center; gap: 4px; font-size: 10px; font-weight: 700; color: var(--success); text-transform: uppercase; letter-spacing: 0.04em; }
  .comp-attached svg { flex-shrink: 0; }
  .comp-unattached { font-size: 10px; color: var(--moonrock); text-transform: uppercase; letter-spacing: 0.04em; }

  /* ── Bound component cards ── */
  .bound-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
  .bound-card {
    background: var(--spotlight);
    border-radius: var(--radius-sm);
    padding: 20px;
    box-shadow: var(--shadow-sm);
    border-top: 3px solid var(--neptune);
    transition: transform 0.2s;
  }
  .bound-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
  .bound-card h4 { font-size: 15px; font-weight: 700; margin-bottom: 10px; }
  .bound-card .bound-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
  .bound-stat { font-size: 12px; color: var(--slate); }
  .bound-stat strong { color: var(--cosmos); font-weight: 600; }
  .bound-card .bound-date { font-size: 11px; color: var(--slate); margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--fog); }

  /* ── Timeline ── */
  .timeline { position: relative; padding-left: 28px; }
  .timeline::before { content: ''; position: absolute; left: 8px; top: 6px; bottom: 6px; width: 2px; background: linear-gradient(to bottom, var(--neptune), var(--diatomite)); border-radius: 1px; }
  .tl-item { position: relative; margin-bottom: 16px; }
  .tl-item::before { content: ''; position: absolute; left: -24px; top: 6px; width: 12px; height: 12px; border-radius: 50%; background: var(--spotlight); border: 3px solid var(--neptune); }
  .tl-item:first-child::before { background: var(--neptune); }
  .tl-date { font-size: 11px; font-weight: 700; color: var(--neptune); text-transform: uppercase; letter-spacing: 0.03em; }
  .tl-text { font-size: 14px; color: #444; margin-top: 2px; }

  /* ── Issues ── */
  .issue-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
  .issue-card {
    border-radius: var(--radius-sm);
    padding: 20px;
    box-shadow: var(--shadow-sm);
    transition: transform 0.2s;
  }
  .issue-card:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); }
  .issue-severity { display: inline-block; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; padding: 2px 8px; border-radius: 4px; margin-bottom: 8px; }
  .issue-card h4 { font-size: 14px; font-weight: 700; margin-bottom: 6px; }
  .issue-card p { font-size: 13px; color: #555; line-height: 1.5; }
  .issue-impact { font-size: 12px; font-weight: 600; margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(0,0,0,0.06); }

  .footer { text-align: center; padding: 32px; font-size: 12px; color: var(--slate); }
  .footer code { background: var(--diatomite); padding: 2px 6px; border-radius: 4px; font-size: 11px; }

  @media (max-width: 900px) {
    .hero-grid { grid-template-columns: repeat(2, 1fr); }
    .grid-2col { grid-template-columns: 1fr; }
    .container { padding: 0 20px 40px; }
    .header { padding: 28px 20px 60px; }
    .pie-layout { flex-direction: column; }
    .bar-file { width: 120px; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>GDS Design Token Migration</h1>
  <p>V2 Token Pipeline &mdash; Dashboard &mdash; ${now}</p>
</div>

<div class="container">

  <!-- ── Hero donuts ── -->
  <div class="hero-grid">
    <div class="hero-card">
      <div class="donut-wrap">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#e8e8ed" stroke-width="10"/>
          <circle cx="50" cy="50" r="40" fill="none" stroke="var(--neptune)" stroke-width="10"
            stroke-dasharray="251.3" stroke-dashoffset="0" stroke-linecap="round"
            transform="rotate(-90 50 50)" class="donut-arc"/>
          <text x="50" y="48" text-anchor="middle" fill="var(--neptune)" font-size="24" font-weight="800">${totalTokens}</text>
          <text x="50" y="62" text-anchor="middle" fill="#949494" font-size="10" font-weight="500">${totalFiles} files</text>
        </svg>
      </div>
      <div class="hero-label">Total Tokens</div>
    </div>

    <div class="hero-card">
      ${svgDonut(mappedPct, '#6366f1', 100, 10, `${mappedPct}%`, `${mappedComponents}/${totalComponents}`)}
      <div class="hero-label">Mapped</div>
    </div>

    <div class="hero-card">
      ${svgDonut(boundPct, '#048851', 100, 10, `${boundPct}%`, `${totalBound}/${totalComponents}`)}
      <div class="hero-label">Token Bound</div>
    </div>

    <div class="hero-card">
      ${svgDonut(verifiedPct, '#e8920d', 100, 10, `${verifiedPct}%`, `${verifiedComponents}/${totalComponents}`)}
      <div class="hero-label">Verified</div>
    </div>
  </div>

  <!-- ── Token inventory ── -->
  <div class="section">
    <div class="section-header"><h2>Token Inventory</h2><div class="section-line"></div></div>
    <div class="grid-2col">
      <div class="panel">
        <h3>Distribution by Tier</h3>
        <div class="pie-layout">
          ${svgPieChart(pieSegments, 160)}
          <div class="pie-legend">
            ${tierOrder
              .filter((t) => tierTotals[t])
              .map(
                (t) =>
                  `<div class="pie-legend-row"><span class="pie-swatch" style="background:${tierColors[t]}"></span><span class="pie-legend-label">${t}</span><span class="pie-legend-value">${tierTotals[t]}</span><span class="pie-legend-pct">${((tierTotals[t] / totalTokens) * 100).toFixed(0)}%</span></div>`
              )
              .join('\n            ')}
          </div>
        </div>
      </div>
      <div class="panel">
        <h3>Tokens per File</h3>
        <div class="bar-chart">
          ${tokenFiles
            .sort((a, b) => b.count - a.count)
            .slice(0, 12)
            .map((f) => {
              const pct = ((f.count / tokenFiles[0].count) * 100).toFixed(0);
              return `<div class="bar-row"><span class="bar-file" title="${f.file}">${f.file.replace(/\.json$/, '')}</span><div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${tierColors[f.tier]}"><span>${f.count}</span></div></div></div>`;
            })
            .join('\n          ')}
        </div>
      </div>
    </div>
  </div>

  <!-- ── Pipeline overview ── -->
  <div class="section">
    <div class="section-header"><h2>Migration Pipeline</h2><div class="section-line"></div></div>
    <div class="panel">
      <div class="pipeline">
        <div class="pipeline-row">
          <span class="pipeline-label">Token Mapping</span>
          <div class="pipeline-track"><div class="pipeline-fill" style="width:${mappedPct}%;background:linear-gradient(90deg, #6366f1, #818cf8)"><span>${mappedComponents} done</span></div></div>
          <span class="pipeline-val" style="color:#6366f1">${mappedPct}%</span>
        </div>
        <div class="pipeline-row">
          <span class="pipeline-label">Token Binding</span>
          <div class="pipeline-track"><div class="pipeline-fill" style="width:${boundPct}%;background:linear-gradient(90deg, #048851, #22c55e)"><span>${totalBound} bound (${totalBindings} bindings)</span></div></div>
          <span class="pipeline-val" style="color:#048851">${boundPct}%</span>
        </div>
        <div class="pipeline-row">
          <span class="pipeline-label">Visual QA</span>
          <div class="pipeline-track"><div class="pipeline-fill" style="width:${verifiedPct || 2}%;background:linear-gradient(90deg, #e8920d, #fbbf24)">${verifiedComponents > 0 ? `<span>${verifiedComponents} done</span>` : ''}</div></div>
          <span class="pipeline-val" style="color:#e8920d">${verifiedPct}%</span>
        </div>
        <div class="pipeline-row">
          <span class="pipeline-label">Storybook</span>
          <div class="pipeline-track"><div class="pipeline-fill" style="width:2%;background:linear-gradient(90deg, #d946ef, #e879f9)"></div></div>
          <span class="pipeline-val" style="color:#d946ef">0%</span>
        </div>
      </div>
    </div>
  </div>

  <!-- ── Priority breakdown ── -->
  <div class="section">
    <div class="section-header"><h2>Progress by Priority</h2><div class="section-line"></div></div>
    <div class="panel">
      <div class="prio-legend-bar" style="margin-bottom:16px;">
        <span><span class="dot" style="background:var(--neptune)"></span> Mapped only</span>
        <span><span class="dot" style="background:var(--success)"></span> Token bound</span>
        <span><span class="dot" style="background:var(--warning)"></span> Partial</span>
        <span><span class="dot" style="background:#f0f1f4"></span> Not started</span>
      </div>
      <div class="prio-chart">
        ${tracker.priorities
          .map((p) => {
            const total = p.components.length;
            const fullNames = BOUND_COMPONENTS.filter((b) => b.status === 'full').map((b) => b.name);
            const partialNames = BOUND_COMPONENTS.filter((b) => b.status === 'partial').map((b) => b.name);
            const resolve = (name) => TRACKER_ALIASES[name] || name;
            const full = p.components.filter((c) => fullNames.includes(resolve(c.name))).length;
            const partial = p.components.filter((c) => partialNames.includes(resolve(c.name))).length;
            const mappedOnly = p.components.filter((c) => c.mapped && !fullNames.includes(resolve(c.name)) && !partialNames.includes(resolve(c.name))).length;
            const remaining = total - full - partial - mappedOnly;
            const boundTotal = full + partial;
            return `<div class="prio-group">
          <div class="prio-group-header"><h4>${p.id.replace('Priority ', 'P')}: ${p.name}</h4><span class="prio-count">${boundTotal}/${total} bound</span></div>
          <div class="prio-stacked-bar">
            ${full > 0 ? `<div class="prio-seg prio-seg-applied" style="flex:${full}" title="${full} fully bound">${full}</div>` : ''}
            ${partial > 0 ? `<div class="prio-seg" style="flex:${partial};background:var(--warning)" title="${partial} partial">${partial}</div>` : ''}
            ${mappedOnly > 0 ? `<div class="prio-seg prio-seg-mapped" style="flex:${mappedOnly}" title="${mappedOnly} mapped">${mappedOnly}</div>` : ''}
            ${remaining > 0 ? `<div class="prio-seg prio-seg-remaining" style="flex:${remaining}"></div>` : ''}
          </div>
        </div>`;
          })
          .join('\n        ')}
      </div>
    </div>
  </div>

  <!-- ── Component map ── -->
  <div class="section">
    <div class="section-header"><h2>Component Map</h2><div class="section-line"></div></div>
    <div class="panel">
      <div style="display:flex;align-items:center;gap:20px;font-size:12px;color:var(--slate);margin-bottom:16px;flex-wrap:wrap;">
        <span>Pipeline stage pips:</span>
        <span style="display:flex;align-items:center;gap:4px;"><span class="comp-pip pip-done" style="width:14px;height:5px;display:inline-block;"></span> Mapped</span>
        <span style="display:flex;align-items:center;gap:4px;"><span class="comp-pip pip-done" style="width:14px;height:5px;display:inline-block;"></span> Figma</span>
        <span style="display:flex;align-items:center;gap:4px;"><span class="comp-pip pip-done" style="width:14px;height:5px;display:inline-block;"></span> Verified</span>
        <span style="display:flex;align-items:center;gap:4px;"><span class="comp-pip pip-done" style="width:14px;height:5px;display:inline-block;"></span> Storybook</span>
        <span style="margin-left:auto;display:flex;align-items:center;gap:6px;"><svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M13.3 4.3a1 1 0 010 1.4l-6 6a1 1 0 01-1.4 0l-3-3a1 1 0 011.4-1.4L6.6 9.6l5.3-5.3a1 1 0 011.4 0z" fill="#048851"/></svg> Fully bound &nbsp; <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5" stroke="#e8920d" stroke-width="2" fill="none"/></svg> Partial</span>
      </div>
      <div class="comp-grid">
        ${tracker.components
          .map((c) => {
            const resolvedName = TRACKER_ALIASES[c.name] || c.name;
            const boundInfo = BOUND_COMPONENTS.find((b) => b.name === resolvedName);
            const isBound = !!boundInfo;
            const isFull = boundInfo && boundInfo.status === 'full';
            const isPartial = boundInfo && boundInfo.status === 'partial';
            const cellClass = isFull ? ' is-bound' : isPartial ? ' is-partial' : '';
            return `<div class="comp-cell${cellClass}">
          <div class="comp-name">${c.name}</div>
          <div class="comp-pips">
            <div class="comp-pip ${c.mapped ? 'pip-done' : 'pip-empty'}" title="Mapped"></div>
            <div class="comp-pip ${isBound ? 'pip-done' : 'pip-empty'}" title="Token Bound"></div>
            <div class="comp-pip ${c.verified ? 'pip-done' : 'pip-empty'}" title="Verified"></div>
            <div class="comp-pip ${c.storybook ? 'pip-done' : 'pip-empty'}" title="Storybook"></div>
          </div>
          ${isFull ? `<div class="comp-attached"><svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M13.3 4.3a1 1 0 010 1.4l-6 6a1 1 0 01-1.4 0l-3-3a1 1 0 011.4-1.4L6.6 9.6l5.3-5.3a1 1 0 011.4 0z" fill="#048851"/></svg> Bound (${boundInfo.bindings})</div>` : isPartial ? `<div class="comp-attached" style="color:var(--warning)"><svg width="12" height="12" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#e8920d" stroke-width="2" fill="none"/><circle cx="8" cy="8" r="2" fill="#e8920d"/></svg> Partial (${boundInfo.bindings})</div>` : `<div class="comp-unattached">Not bound</div>`}
        </div>`;
          })
          .join('\n        ')}
      </div>
    </div>
  </div>

  <!-- ── Bound component detail ── -->
  <div class="section">
    <div class="section-header"><h2>Token Bound Components</h2><div class="section-line"></div></div>
    <div class="bound-grid">
      ${BOUND_COMPONENTS.map(
        (bc) => {
          const statusColor = bc.status === 'full' ? '#048851' : '#e8920d';
          const statusBg = bc.status === 'full' ? '#ecfdf5' : '#fffbeb';
          const statusLabel = bc.status === 'full' ? 'Bound' : 'Partial';
          const tokenFile = TOKEN_FILE_COMPONENTS.find((t) => t.name === bc.name);
          return `<div class="bound-card" style="border-top-color:${statusColor}">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
          <h4 style="margin:0">${bc.name}</h4>
          <span style="display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:700;color:${statusColor};background:${statusBg};padding:3px 8px;border-radius:10px;text-transform:uppercase;letter-spacing:0.04em;">
            ${bc.status === 'full' ? `<svg width="10" height="10" viewBox="0 0 16 16" fill="none"><path d="M13.3 4.3a1 1 0 010 1.4l-6 6a1 1 0 01-1.4 0l-3-3a1 1 0 011.4-1.4L6.6 9.6l5.3-5.3a1 1 0 011.4 0z" fill="${statusColor}"/></svg>` : `<svg width="10" height="10" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5" stroke="${statusColor}" stroke-width="2" fill="none"/></svg>`}
            ${statusLabel}
          </span>
        </div>
        <div class="bound-stats">
          <div class="bound-stat">Bindings: <strong>${bc.bindings}</strong></div>
          <div class="bound-stat">Unique tokens: <strong>${bc.uniqueTokens}</strong></div>
          ${tokenFile ? `<div class="bound-stat">Token file: <strong>${tokenFile.file.replace('component/', '')}</strong></div>` : ''}
          <div class="bound-stat">Method: <strong>Token Studio</strong></div>
        </div>
        <div style="margin-top:8px;font-size:11px;color:var(--slate);">${bc.properties}</div>
      </div>`;
        }
      ).join('\n      ')}
    </div>
  </div>

  <!-- ── Recent activity + Issues side by side ── -->
  <div class="section">
    <div class="grid-2col">
      <div>
        <div class="section-header"><h2>Recent Activity</h2><div class="section-line"></div></div>
        <div class="panel">
          <div class="timeline">
            ${RECENT_ACTIVITY.map(
              (a) => `<div class="tl-item"><div class="tl-date">${a.date}</div><div class="tl-text">${a.item}</div></div>`
            ).join('\n            ')}
          </div>
        </div>
      </div>
      <div>
        <div class="section-header"><h2>Known Issues</h2><div class="section-line"></div></div>
        <div class="issue-grid" style="grid-template-columns:1fr;">
          ${KNOWN_ISSUES.map(
            (issue) => `<div class="issue-card" style="background:${severityBg[issue.severity]}">
            <span class="issue-severity" style="color:${severityColors[issue.severity]};background:${severityColors[issue.severity]}15">${issue.severity}</span>
            <h4>${issue.title}</h4>
            <p>${issue.detail}</p>
            <div class="issue-impact" style="color:${severityColors[issue.severity]}">Impact: ${issue.impact}</div>
          </div>`
          ).join('\n          ')}
        </div>
      </div>
    </div>
  </div>

</div>

<div class="footer">
  GDS Design Token Migration Dashboard &mdash; <code>node scripts/build-dashboard.js</code> &mdash; ${now}
</div>

</body>
</html>`;
}

// ── Main ────────────────────────────────────────────────────────────────────

function main() {
  const tokenFiles = collectTokenFiles();
  const tracker = parseTracker();

  if (!fs.existsSync(BUILD_DIR)) fs.mkdirSync(BUILD_DIR, { recursive: true });

  const html = generateHtml(tokenFiles, tracker);
  const outPath = path.join(BUILD_DIR, 'dashboard.html');
  fs.writeFileSync(outPath, html, 'utf8');

  console.log(`Dashboard generated: ${outPath}`);
  console.log(`  Tokens: ${tokenFiles.reduce((s, f) => s + f.count, 0)} across ${tokenFiles.length} files`);
  console.log(`  Components: ${tracker.components.length} tracked`);
}

main();
