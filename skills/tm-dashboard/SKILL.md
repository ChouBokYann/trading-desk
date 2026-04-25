---
name: tm-dashboard
description: Generate live portfolio telemetry dashboard. Use when the user requests 'dashboard', 'telemetry', 'portfolio view', or 'show positions'.
---

# The Money -- Dashboard

## Overview

This skill generates a single-file HTML dashboard showing everything a trader needs at a glance -- the F1 telemetry concept. It shows what's ABOUT to happen (distance to stop, theta decay today, correlation spikes), not just what already happened. No server, no dependencies beyond a browser.

Act as a telemetry engineer. Gather data from every source, structure it, and render a dashboard that surfaces risk and opportunity at a glance. Highlight what needs attention -- don't bury warnings in tables.

**Module:** `tm` (The Money)

**Sections:** Portfolio overview, Greeks, correlation heatmap, risk telemetry, regime strip, strategy allocation, performance sparklines, active watchlist, confirmation queue.

**Args:** Optional section name to render just one panel (e.g., `risk`, `greeks`, `watchlist`). No args = full dashboard.

## Conventions

- Bare paths (e.g. `references/guide.md`) resolve from the skill root.
- `{project-root}`-prefixed paths resolve from the project working directory.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` (root level and `tm` section). If config is missing, let the user know `tm-setup` can configure the module at any time. Use sensible defaults for anything not configured.

Route by args:

- No args -> full dashboard (below)
- Section name -> render that section only, same data gathering but limited output

## Dashboard Generation

### Step 1: Gather Data

Pull from all sources in parallel where possible. Load `references/data-gathering.md` for the full data source map and structure requirements.

### Step 2: Generate HTML

Pass the structured data to the dashboard generator:

```
python scripts/generate_dashboard.py -o {project-root}/_bmad-output/dashboard.html
```

The script reads JSON from stdin. Feed it the gathered data as a JSON object with keys matching the section names. See `scripts/generate_dashboard.py --help` for the expected schema.

### Step 3: Open and Brief

Open the generated HTML in the default browser. Give the user a brief verbal summary of what needs attention -- any red flags, TCAS warnings, positions approaching stops, or decay-flagged positions. Two to three sentences, not a wall of text.
