# Strategy Session

A collaborative conversation to design, refine, or update trading rules with quantitative justification.

## What Success Looks Like

The session produces one or more of:
- New or updated strategy rules written to wiki strategy pages
- Daemon-executable rule files (via Rule Authoring capability)
- Updated conviction tiers or source weights
- Wiki entries capturing the reasoning for future reference

## Approach

Start by understanding what the user wants to explore — a new strategy idea, refining an existing one, or responding to performance data. Then:

- Ground every discussion in evidence: wiki playbook history, quant layer EV data, regime context
- Challenge assumptions — if the user proposes a rule, ask what evidence supports it and what would falsify it
- Ensure every rule is testable: clear entry conditions, exit conditions, and measurable expected outcome
- Write rules in the format the daemon can parse (load `references/rule-format.md` when ready to write)
- Update relevant wiki pages with the strategic reasoning — future sessions need this context

## Key Constraints

- No rule change without citing evidence from the wiki or quant layer (or explicitly flagging it as hypothesis needing paper-trade validation)
- New strategies require 100-trade paper proof before real capital allocation (Q8 from brainstorming)
- Strategy changes during drawdowns require extra scrutiny — flag if the user is reacting to recent losses rather than evidence
