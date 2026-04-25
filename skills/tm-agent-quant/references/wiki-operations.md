# Wiki Operations

Maintain the health, accuracy, and cross-referencing of The Money's LLM wiki.

## What Success Looks Like

A wiki where every page is current, cross-referenced, and confidence-rated. No orphan pages, no stale claims, no contradictions. The knowledge compounds rather than rots.

## Operations

**Lint** — Scan the full wiki for:
- Contradictions between pages (e.g., regime playbook says X, strategy page says opposite)
- Stale pages: confidence decay past threshold (high→medium after 90 days, medium→low after 60)
- Orphan pages with no inbound `[[wikilinks]]`
- Pages referenced via `[[wikilink]]` that don't exist yet (creation candidates)
- Missing cross-references between related pages
- Causal factor pages not linked from relevant post-mortems

**Update** — Modify existing wiki pages with new information. Follow the schema conventions in `{project-root}/_bmad/memory/tm/schema.md`: update frontmatter (especially `updated` date and `confidence`), maintain cross-links, append to `wiki/log.md`.

**Cross-Reference** — After any wiki change, verify that all `[[wikilinks]]` in modified pages point to real pages, and that related pages link back. The wiki is a network, not a filing cabinet.

**Index Refresh** — Rebuild `wiki/index.md` to reflect current page inventory with accurate descriptions and source counts.
