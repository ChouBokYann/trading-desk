# Wiki Lint

Health check for the wiki knowledge base. Detects structural issues that degrade knowledge quality over time.

## Checks

### 1. Stale Pages

Scan all wiki pages for `updated` dates older than 30 days (configurable). Pages that haven't been updated despite new trades in their domain are candidates for refresh.

Exclude `raw/` (immutable by design).

### 2. Orphan Pages

Find wiki pages that aren't referenced from any other page or from `index.md`. Orphans represent knowledge that's disconnected from the rest of the system.

### 3. Missing Cross-References

For each page's `related` field, verify the referenced pages exist. For each causal factor tag in trade logs, verify a corresponding factor page exists.

### 4. Contradictions

Look for conflicting claims across pages. Common patterns:
- A regime playbook says "sell premium in VIX spikes" but a strategy page says "avoid options in high VIX"
- A ticker page has a bullish thesis but the sector page flags the sector as rotating out
- Confidence levels that should have decayed but haven't

### 5. Index Completeness

Verify `wiki/index.md` catalogs every page in the wiki. Any page not listed is invisible to The Quant on activation.

### 6. Schema Compliance

Verify all wiki pages have valid frontmatter per `wiki/schema.md`: required fields present, types match, dates parseable.

## Output

Present a lint report:

```
WIKI LINT REPORT
================
Pages scanned:    {count}
Stale (>30d):     {count} — {list}
Orphans:          {count} — {list}
Missing refs:     {count} — {details}
Contradictions:   {count} — {details}
Index gaps:       {count} — {list}
Schema issues:    {count} — {details}

Health score: {score}/100
```

For each finding, include the specific page and a recommended fix. Offer to auto-fix index gaps and missing cross-references (these are safe, additive operations). Flag contradictions and stale pages for human review.

Update `wiki/log.md`:
```
[{date}] LINT: Wiki health {score}/100. {issues_found} issues found, {auto_fixed} auto-fixed.
```
