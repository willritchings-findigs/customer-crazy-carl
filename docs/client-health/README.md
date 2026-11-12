# Client Health documentation

Two documents, published to Notion (RevOps wiki › ❤️ Account Health & Sentiment):

| Source | Notion page | Audience |
|---|---|---|
| `design.md` | [Client Health Dashboard: how it works](https://app.notion.com/p/416335d59add81748f99db6050a3b77b) | CS/CX leadership, maintainers |
| `am-guide.md` | [How to read your Client Health scores](https://app.notion.com/p/416335d59add81a38998ddfdece7cd32) | Account managers, CSAs |

**The repo is the source; Notion is the published copy.** Don't edit the Notion pages directly:
the next republish overwrites them.

## What is generated vs hand-written

- Blocks between `<!-- BEGIN GENERATED: x -->` and `<!-- END GENERATED: x -->` are produced by
  `build_docs.py` from `.claude/skills/client-health-refresh/config.json` (every threshold,
  weight, roll-up rule, safeguard, alert rule, Gong title rule) and `metrics_catalog.json`
  (metric definitions). Never edit them by hand.
- Everything else is hand-written narrative.

## When to update

| Change | Do this |
|---|---|
| A threshold, weight, rule or Gong pattern in `config.json` | `python3 docs/client-health/build_docs.py`, review the diff, commit, republish |
| A metric's meaning or source | Edit `metrics_catalog.json`, regenerate, commit, republish |
| Architecture, sources, outputs, open items | Edit the `.md` narrative, commit, republish |

## Republishing to Notion

Replace each page's content with its `.md` file after: removing the `GENERATED` marker lines,
replacing `<br>` with `<br />`, escaping `#p-<company>` outside code as `#p-&lt;company&gt;`, and
dropping the first line (the title; it is the page title in Notion).
