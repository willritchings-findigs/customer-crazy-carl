# Support Metrics documentation

Two documents, published to Notion (RevOps wiki › ❤️ Account Health & Sentiment), next to the
Client Health pair:

| Source | Notion page | Audience |
|---|---|---|
| `design.md` | [Support Metrics Dashboard: how it works](https://app.notion.com/p/416335d59add813ab572c4f8396a1166) | CS/CX leadership, maintainers |
| `reader-guide.md` | [How to read the Support Metrics dashboard](https://app.notion.com/p/416335d59add8127aadbe0906e54446b) | Support leads, agents |

**The repo is the source; Notion is the published copy.** Don't edit the Notion pages directly:
the next republish overwrites them.

These pages are hand-written (no generated blocks). Every rule they state lives in
`.claude/skills/support-metrics-refresh/config.json`: after changing a rule there, update the matching line
here in the same commit and republish.

## Republishing to Notion

Replace each page's content with its `.md` file after: replacing `<br/>` with `<br />`, turning
the companion-page link into a Notion page mention, and dropping the first line (the title; it is
the page title in Notion).
