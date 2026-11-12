# Churn Analysis documentation

Two documents, published to Notion (RevOps wiki › ❤️ Account Health & Sentiment), next to the
Client Health pair:

| Source | Notion page | Audience |
|---|---|---|
| `design.md` | [Churn Analysis Dashboard: how it works](https://app.notion.com/p/416335d59add81948d09f872988a5bf1) | CS/CX leadership, maintainers |
| `reader-guide.md` | [How to read the Churn Analysis dashboard](https://app.notion.com/p/416335d59add81f0936fdf490fc6d3fd) | Account managers, CSAs |

**The repo is the source; Notion is the published copy.** Don't edit the Notion pages directly:
the next republish overwrites them.

These pages are hand-written (no generated blocks). Every rule they state lives in
`.claude/skills/churn-analysis-refresh/config.json`: after changing a rule there, update the matching line
here in the same commit and republish.

## Republishing to Notion

Replace each page's content with its `.md` file after: replacing `<br/>` with `<br />`, turning
the companion-page link into a Notion page mention, and dropping the first line (the title; it is
the page title in Notion).
