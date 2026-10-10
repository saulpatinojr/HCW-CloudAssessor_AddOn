# User guide

The Cloud Assessment pane reads one file: an export of your Azure resources from Resource Graph. It never asks for
credentials and never connects to your cloud; the file is processed in memory, the results are returned only to your
browser session, and everything expires after two hours or when you delete it.

## 1. Export your resources

**Azure CLI** (bash or PowerShell; needs the `resource-graph` extension and `Reader` on the scope):

```bash
az extension add --name resource-graph --upgrade --only-show-errors
az graph query -q "resources | project id,name,type,location,resourceGroup,subscriptionId,tags,properties,sku,identity,kind" --first 1000 -o json > resources.json
```

PowerShell:

```powershell
az extension add --name resource-graph --upgrade --only-show-errors
az graph query -q "resources | project id,name,type,location,resourceGroup,subscriptionId,tags,properties,sku,identity,kind" --first 1000 -o json | Set-Content -Encoding utf8 resources.json
```

The command prints the `az graph query` envelope (`count`, `data`, `skip_token`, `total_records`); the pane accepts it
as is, or a bare array. If `skip_token` is not null the export is paged and the pane warns that only the first page was
uploaded (`--first 1000` is the CLI's maximum per page; narrow the query with `| where subscriptionId == '…'` or
`| where resourceGroup == '…'` if the estate is larger).

**Portal, Resource Graph Explorer**: `https://portal.azure.com/#view/HubsExtension/ArgQueryBlade`, paste the same
query, **Run query**, then **Download as CSV**. The CSV has the same columns with JSON in the `tags`, `properties`,
`sku` and `identity` cells; the pane parses them.

**Portal, All resources** (`https://portal.azure.com/#view/HubsExtension/BrowseAll`, **Export to CSV**) is accepted
too, with the warning "no properties column": it carries names, types, groups and locations only, so almost every
criterion answers `unknown`. That is the honest answer; use one of the two exports above to assess configuration.

Limits: 5 MB, 5,000 rows.

## 2. Upload and run

Drop the file on the pane (or choose it, or use the sample). The pane detects the format, shows the first five rows and
any warnings, asks you to complete the human verification, then **Run assessment**. The upload is processed in memory
and answered within seconds.

## 3. Read the scorecard

One card per framework (FinOps, Well-Architected cost optimisation, Zero Trust) with its pillars. Each card shows a
score, a coverage figure and the sentence "Score covers N of M checks; K could not be assessed from an export".
**Unknown never lowers a score; it lowers coverage.** A high score with low coverage is a question, not an answer.
Pillar weights come from the catalog; a request may override them within 0 to 10.

## 4. Work the findings

Filter by framework, severity and state (fail, pass, unknown, not applicable), or search by resource or criterion.
Open a finding to see the evidence path, the observed and expected values, the remediation and the reference link
(all links point at `learn.microsoft.com` or `www.finops.org`; every link is marked for verification until the owner
confirms it).

## 5. What the export cannot show

The "Unknown by design" panel lists what no Resource Graph export carries, and the criteria that answer `unknown` for
that reason: spend and forecasts; budgets and cost alerts (not in the `resources` table unless exported from their own
table); role assignments and Entra posture; diagnostic settings; policy compliance; subscription-level Defender plans;
network flow and private DNS resolution.

## 6. Take the results with you, then delete them

**Download bundle** saves `assessment-<id>.zip` (`report.md`, `report.json`, `findings.csv`, `NOT-AN-AUDIT.md`). If a
download cannot start inside the embedded pane, **Copy report** puts the Markdown report on the clipboard and the report
is shown in a selectable block. **Delete my data now** removes the assessment immediately; otherwise it expires after
two hours. This is not an audit (see `NOT-AN-AUDIT.md`).
