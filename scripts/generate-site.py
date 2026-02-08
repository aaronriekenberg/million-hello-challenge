#!/usr/bin/env python3
"""
Parse results/raw.md and generate a professional static website with Chart.js bar charts.
Output is written to _site/index.html for GitHub Pages deployment.
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_MD = os.path.join(REPO_ROOT, "results", "raw.md")
SITE_DIR = os.path.join(REPO_ROOT, "_site")


def parse_raw_md(path):
    with open(path) as f:
        content = f.read()

    # Extract timestamp
    ts_match = re.search(r"## Timestamp\s*\n(.+)", content)
    timestamp = ts_match.group(1).strip() if ts_match else "Unknown"

    # Extract hardware info table
    hw_match = re.search(
        r"\| CPU Model \|.*\n\| [-\s|]+\n\|(.+)\|", content
    )
    hardware = {}
    if hw_match:
        parts = [c.strip() for c in hw_match.group(1).split("|")]
        hardware = {
            "cpu_model": parts[0] if len(parts) > 0 else "",
            "num_cpus": parts[1] if len(parts) > 1 else "",
            "memory": parts[2] if len(parts) > 2 else "",
        }

    # Extract benchmark rows
    rows = []
    bench_section = content.split("## Benchmarks of 1 Million Requests")
    if len(bench_section) < 2:
        print("ERROR: Could not find benchmarks section", file=sys.stderr)
        sys.exit(1)

    table_lines = bench_section[1].strip().split("\n")
    for line in table_lines[2:]:  # skip header + separator
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 12:
            continue
        rows.append(
            {
                "name": cols[0],
                "connections": int(cols[1]),
                "success_rate": cols[2],
                "test_seconds": float(cols[3]),
                "rps": float(cols[4]),
                "p50": float(cols[5]),
                "p99": float(cols[6]),
                "p999": float(cols[7]),
                "memory_mb": float(cols[8]),
                "cpu_time": cols[9],
                "threads": int(cols[10]),
                "processes": int(cols[11]),
            }
        )

    return {
        "timestamp": timestamp,
        "hardware": hardware,
        "results": rows,
    }


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Million Hello Challenge - Benchmark Results</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<script>
  // Apply theme immediately to prevent flash
  (function() {
    const saved = localStorage.getItem('theme');
    if (saved) { document.documentElement.setAttribute('data-theme', saved); }
    else if (window.matchMedia('(prefers-color-scheme: light)').matches) { document.documentElement.setAttribute('data-theme', 'light'); }
  })();
</script>
<style>
  :root, [data-theme="dark"] {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #1c2333;
    --border: #30363d;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --accent-rust: #dea584;
    --accent-go: #00add8;
    --accent-kotlin: #a97bff;
    --accent-node: #5fa04e;
    --accent-python: #3572a5;
    --accent-blue: #58a6ff;
    --accent-green: #3fb950;
    --accent-orange: #d29922;
    --hero-gradient: linear-gradient(135deg, #0d1117 0%, #1a1f35 50%, #0d1117 100%);
    --chart-text: #8b949e;
    --chart-grid: rgba(48,54,61,0.5);
    --tooltip-bg: #1c2333;
    --tooltip-text: #e6edf3;
    --tooltip-border: #30363d;
    --hover-row: rgba(88, 166, 255, 0.04);
  }
  [data-theme="light"] {
    --bg-primary: #ffffff;
    --bg-secondary: #f6f8fa;
    --bg-card: #eef1f5;
    --border: #d0d7de;
    --text-primary: #1f2328;
    --text-secondary: #656d76;
    --accent-rust: #b35a2a;
    --accent-go: #007d9c;
    --accent-kotlin: #7f52ff;
    --accent-node: #3c7a2f;
    --accent-python: #2b5b84;
    --accent-blue: #0969da;
    --accent-green: #1a7f37;
    --accent-orange: #9a6700;
    --hero-gradient: linear-gradient(135deg, #f0f3f6 0%, #dfe6ed 50%, #f0f3f6 100%);
    --chart-text: #656d76;
    --chart-grid: rgba(208,215,222,0.6);
    --tooltip-bg: #ffffff;
    --tooltip-text: #1f2328;
    --tooltip-border: #d0d7de;
    --hover-row: rgba(9, 105, 218, 0.04);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
  }
  .hero {
    background: var(--hero-gradient);
    border-bottom: 1px solid var(--border);
    padding: 3rem 2rem;
    text-align: center;
    position: relative;
  }
  .hero h1 {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-kotlin), var(--accent-rust));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
  }
  .theme-toggle {
    position: absolute;
    top: 1.2rem;
    right: 1.5rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.45rem 0.75rem;
    cursor: pointer;
    color: var(--text-secondary);
    font-size: 1.15rem;
    line-height: 1;
    transition: background 0.2s, border-color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }
  .theme-toggle:hover {
    background: var(--bg-card);
    border-color: var(--accent-blue);
    color: var(--text-primary);
  }
  .theme-toggle .label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .hero p {
    color: var(--text-secondary);
    font-size: 1.1rem;
    max-width: 700px;
    margin: 0 auto;
  }
  .container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
  }
  .meta-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 2rem;
    padding: 1rem 1.5rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 8px;
  }
  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .meta-label {
    color: var(--text-secondary);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }
  .meta-value {
    color: var(--text-primary);
    font-size: 0.95rem;
    font-weight: 500;
  }
  .section-title {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .section-title .icon {
    font-size: 1.2rem;
  }
  .charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  .chart-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    transition: border-color 0.2s;
  }
  .chart-card:hover {
    border-color: #58a6ff44;
  }
  .chart-card h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text-secondary);
  }
  .chart-wrapper {
    position: relative;
    width: 100%;
    height: 340px;
  }
  .chart-card.full-width {
    grid-column: 1 / -1;
  }
  .chart-card.full-width .chart-wrapper {
    height: 400px;
  }
  .table-section {
    margin-top: 2rem;
  }
  .table-wrap {
    overflow-x: auto;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }
  thead th {
    position: sticky;
    top: 0;
    background: var(--bg-card);
    color: var(--text-secondary);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    font-size: 0.75rem;
    padding: 0.85rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }
  tbody td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }
  tbody tr:last-child td {
    border-bottom: none;
  }
  tbody tr:hover {
    background: var(--hover-row);
  }
  .lang-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: capitalize;
  }
  .lang-badge.rust   { background: rgba(222,165,132,0.15); color: var(--accent-rust); }
  .lang-badge.go     { background: rgba(0,173,216,0.15);   color: var(--accent-go); }
  .lang-badge.kotlin { background: rgba(169,123,255,0.15); color: var(--accent-kotlin); }
  .lang-badge.node   { background: rgba(95,160,78,0.15);   color: var(--accent-node); }
  .lang-badge.python { background: rgba(53,114,165,0.15);  color: var(--accent-python); }
  .num-cell { font-variant-numeric: tabular-nums; text-align: right; }
  footer {
    text-align: center;
    padding: 2rem;
    color: var(--text-secondary);
    font-size: 0.85rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
  }
  footer a { color: var(--accent-blue); text-decoration: none; }
  footer a:hover { text-decoration: underline; }
  @media (max-width: 900px) {
    .charts-grid { grid-template-columns: 1fr; }
    .hero h1 { font-size: 1.8rem; }
    .container { padding: 1rem; }
  }
</style>
</head>
<body>

<div class="hero">
  <button class="theme-toggle" id="themeToggle" aria-label="Toggle theme">
    <span class="icon" id="themeIcon">&#x1F319;</span>
    <span class="label" id="themeLabel">Dark</span>
  </button>
  <h1>Million Hello Challenge</h1>
  <p>Benchmarking 1 million HTTP &ldquo;Hello World&rdquo; requests across Rust, Go, Kotlin, Node.js, and Python in GitHub Actions.</p>
</div>

<div class="container">

  <div class="meta-bar" id="metaBar"></div>

  <h2 class="section-title"><span class="icon">&#x1F4CA;</span> Performance Overview</h2>

  <div class="charts-grid">
    <div class="chart-card full-width">
      <h3>Requests per Second (higher is better)</h3>
      <div class="chart-wrapper"><canvas id="chartRPS"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>Median Latency &mdash; P50 (lower is better)</h3>
      <div class="chart-wrapper"><canvas id="chartP50"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>P99 Latency (lower is better)</h3>
      <div class="chart-wrapper"><canvas id="chartP99"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>Memory Usage &mdash; MB (lower is better)</h3>
      <div class="chart-wrapper"><canvas id="chartMem"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>Test Duration &mdash; Seconds (lower is better)</h3>
      <div class="chart-wrapper"><canvas id="chartDuration"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>Threads</h3>
      <div class="chart-wrapper"><canvas id="chartThreads"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>Processes</h3>
      <div class="chart-wrapper"><canvas id="chartProcesses"></canvas></div>
    </div>
  </div>

  <div class="table-section">
    <h2 class="section-title"><span class="icon">&#x1F4CB;</span> Full Results</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Language</th>
            <th>Connections</th>
            <th>Success</th>
            <th>Duration (s)</th>
            <th>Req/s</th>
            <th>P50 (ms)</th>
            <th>P99 (ms)</th>
            <th>P99.9 (ms)</th>
            <th>Memory (MB)</th>
            <th>CPU Time</th>
            <th>Threads</th>
            <th>Processes</th>
          </tr>
        </thead>
        <tbody id="resultsBody"></tbody>
      </table>
    </div>
  </div>

</div>

<footer>
  <a href="https://github.com/aaronriekenberg/million-hello-challenge" target="_blank" rel="noopener">
    github.com/aaronriekenberg/million-hello-challenge
  </a>
</footer>

<script>
const DATA = __DATA_PLACEHOLDER__;

const LANG_COLORS = {
  rust:   { bg: 'rgba(222,165,132,0.85)', border: '#dea584' },
  go:     { bg: 'rgba(0,173,216,0.85)',   border: '#00add8' },
  kotlin: { bg: 'rgba(169,123,255,0.85)', border: '#a97bff' },
  node:   { bg: 'rgba(95,160,78,0.85)',   border: '#5fa04e' },
  python: { bg: 'rgba(53,114,165,0.85)',  border: '#3572a5' },
};

const LANG_ORDER = ['rust', 'go', 'kotlin', 'node', 'python'];
const CONN_LEVELS = [200, 400, 800];

// --- Meta bar ---
(function renderMeta() {
  const bar = document.getElementById('metaBar');
  const hw = DATA.hardware;
  const items = [
    ['Last Run', DATA.timestamp],
    ['CPU', hw.cpu_model],
    ['vCPUs', hw.num_cpus],
    ['Memory', hw.memory],
  ];
  bar.innerHTML = items.map(([l, v]) =>
    `<div class="meta-item"><span class="meta-label">${l}</span><span class="meta-value">${v}</span></div>`
  ).join('');
})();

// --- Table ---
(function renderTable() {
  const tbody = document.getElementById('resultsBody');
  tbody.innerHTML = DATA.results.map(r => `
    <tr>
      <td><span class="lang-badge ${r.name}">${r.name}</span></td>
      <td class="num-cell">${r.connections}</td>
      <td class="num-cell">${r.success_rate}</td>
      <td class="num-cell">${r.test_seconds.toFixed(1)}</td>
      <td class="num-cell">${r.rps.toLocaleString(undefined, {maximumFractionDigits:1})}</td>
      <td class="num-cell">${r.p50.toFixed(4)}</td>
      <td class="num-cell">${r.p99.toFixed(4)}</td>
      <td class="num-cell">${r.p999.toFixed(4)}</td>
      <td class="num-cell">${r.memory_mb.toFixed(1)}</td>
      <td>${r.cpu_time}</td>
      <td class="num-cell">${r.threads}</td>
      <td class="num-cell">${r.processes}</td>
    </tr>`).join('');
})();

// --- Chart helpers ---
function getVal(lang, conns, key) {
  const row = DATA.results.find(r => r.name === lang && r.connections === conns);
  return row ? row[key] : 0;
}

// --- Theme toggle ---
function getThemeColors() {
  const s = getComputedStyle(document.documentElement);
  return {
    chartText: s.getPropertyValue('--chart-text').trim(),
    chartGrid: s.getPropertyValue('--chart-grid').trim(),
    tooltipBg: s.getPropertyValue('--tooltip-bg').trim(),
    tooltipText: s.getPropertyValue('--tooltip-text').trim(),
    tooltipBorder: s.getPropertyValue('--tooltip-border').trim(),
  };
}

function currentTheme() {
  return document.documentElement.getAttribute('data-theme') || 'dark';
}

function updateToggleUI() {
  const dark = currentTheme() === 'dark';
  document.getElementById('themeIcon').innerHTML = dark ? '&#x1F319;' : '&#x2600;&#xFE0F;';
  document.getElementById('themeLabel').textContent = dark ? 'Dark' : 'Light';
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  updateToggleUI();
  rebuildCharts();
}

document.getElementById('themeToggle').addEventListener('click', () => {
  setTheme(currentTheme() === 'dark' ? 'light' : 'dark');
});

window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', e => {
  if (!localStorage.getItem('theme')) {
    document.documentElement.setAttribute('data-theme', e.matches ? 'light' : 'dark');
    updateToggleUI();
    rebuildCharts();
  }
});

updateToggleUI();

function getChartDefaults() {
  const tc = getThemeColors();
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: tc.chartText, font: { size: 12 }, padding: 16, usePointStyle: true, pointStyle: 'rectRounded' },
      },
      tooltip: {
        backgroundColor: tc.tooltipBg,
        titleColor: tc.tooltipText,
        bodyColor: tc.tooltipText,
        borderColor: tc.tooltipBorder,
        borderWidth: 1,
        padding: 10,
        cornerRadius: 6,
      },
    },
    scales: {
      x: {
        ticks: { color: tc.chartText, font: { size: 11 } },
        grid: { color: tc.chartGrid },
      },
      y: {
        ticks: { color: tc.chartText, font: { size: 11 } },
        grid: { color: tc.chartGrid },
        beginAtZero: true,
      },
    },
  };
}

const chartInstances = [];

function makeGroupedBarChart(canvasId, metric, yLabel, opts) {
  opts = opts || {};
  const defaults = getChartDefaults();
  const tc = getThemeColors();
  const datasets = LANG_ORDER.map(lang => ({
    label: lang.charAt(0).toUpperCase() + lang.slice(1),
    data: CONN_LEVELS.map(c => getVal(lang, c, metric)),
    backgroundColor: LANG_COLORS[lang].bg,
    borderColor: LANG_COLORS[lang].border,
    borderWidth: 1,
    borderRadius: 4,
  }));

  const yAxis = { ...defaults.scales.y, title: { display: true, text: yLabel, color: tc.chartText } };
  if (opts.integerOnly) {
    yAxis.ticks = { ...yAxis.ticks, stepSize: 1, callback: v => Number.isInteger(v) ? v : '' };
  }

  const chart = new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: {
      labels: CONN_LEVELS.map(c => c + ' conns'),
      datasets,
    },
    options: {
      ...defaults,
      scales: {
        ...defaults.scales,
        y: yAxis,
      },
    },
  });
  chartInstances.push({ chart, canvasId, metric, yLabel, opts });
}

function rebuildCharts() {
  const specs = chartInstances.map(c => ({ canvasId: c.canvasId, metric: c.metric, yLabel: c.yLabel, opts: c.opts }));
  chartInstances.forEach(c => c.chart.destroy());
  chartInstances.length = 0;
  specs.forEach(s => makeGroupedBarChart(s.canvasId, s.metric, s.yLabel, s.opts));
}

makeGroupedBarChart('chartRPS', 'rps', 'Requests / Second');
makeGroupedBarChart('chartP50', 'p50', 'Milliseconds');
makeGroupedBarChart('chartP99', 'p99', 'Milliseconds');
makeGroupedBarChart('chartMem', 'memory_mb', 'MB');
makeGroupedBarChart('chartDuration', 'test_seconds', 'Seconds');
makeGroupedBarChart('chartThreads', 'threads', 'Threads');
makeGroupedBarChart('chartProcesses', 'processes', 'Processes', { integerOnly: true });
</script>
</body>
</html>"""


def main():
    data = parse_raw_md(RAW_MD)
    os.makedirs(SITE_DIR, exist_ok=True)
    html = HTML_TEMPLATE.replace("__DATA_PLACEHOLDER__", json.dumps(data))
    out_path = os.path.join(SITE_DIR, "index.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
