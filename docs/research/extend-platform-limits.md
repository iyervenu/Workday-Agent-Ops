# Workday Extend platform limits

Researched 2026-10-28. Primary source is **Workday's own Extend developer course manual** on
`doc.workday.com/workday-education` — tier **W** in the provenance key in
[flex-credits-economics.md](flex-credits-economics.md). Items from a weaker source are marked.

## Read this first: two different features, two different limit sets

Workday's admin guide carries a page titled **"Reference: Custom Object and Field Limits"** quoting 200
active custom fields per object, 255-character text fields, 5,000-character paragraph text, 1,500 instances
in the UI and 10,000 via REST.

**Those are the older tenant-configuration "custom objects" feature — NOT Workday Extend business objects.**
The page's only mention of Extend is incidental (UI truncation past 100 custom fields on an effective-dated
object). Quoting those figures as Extend limits is a visible error; the numbers below are the Extend ones.

## Per business object

| Limit | Value |
|---|---|
| Fields | **50** |
| Derived fields | **40** |
| Indexable fields | **5** — in addition to `SINGLE_INSTANCE` fields Extend indexes automatically |
| `SINGLE_INSTANCE` + `MULTI_INSTANCE` combined | **10** |
| `secureByTarget` fields | **1** `R` — reported from the same Workday doc family; not confirmed in the page text we retrieved |

## Per app

| Limit | Value |
|---|---|
| Security domains | **10** |
| `SINGLE_INSTANCE`/`MULTI_INSTANCE` fields targeting a Workday-delivered BO | **25** `R` — reported, not confirmed in retrieved page text |
| Business objects | **No documented limit** |

A default security domain must be identified when creating model component business objects. Without
contextual security, only **public or unconstrained groups** can be added to an app's security domains.

## Per tenant

**10 million instances**, shared across *all* Extend business objects **and attachment objects** in the
tenant. This is the one ceiling that can be consumed by someone else's app.

## Runtime limits

| Limit | Value |
|---|---|
| API `limit` parameter | default **20**, maximum **100** |
| Endpoint response size | **25,000,000 bytes** |
| Endpoint timeout | **24 seconds** |
| Page timeout (whole page) | **60 seconds** |
| WQL with no `LIMIT` clause | returns up to **1,000,000 rows** |
| Endpoints per page | **No documented limit** — bounded in practice by the page timeout |

## Reserved field names

Cannot be used as field names. Case-sensitive: `attachmentContent`, `contentType`, `descriptor`,
`displayID`, `filename`, `fileLength`, `id`, `wid`, `workdayID`. Case-insensitive: SQL keywords.
For `SINGLE_INSTANCE` or indexed fields, additionally: `offset`, `bulk`, `search`, `sort`, `type`, `view`,
`name`.

## Deployment and lifecycle

- **Model components ride the Weekly Service Update.** Apps with model components *"can only be installed on
  Implementation, Sandbox, or Production tenants after the model components of the app deploy to the tenant
  as part of Workday's Weekly Service Update,"* and you *"must promote your app before a weekly deadline
  for new or updated model components."*
- **You cannot push a new business object to production on demand.** This sets the cadence of any Extend
  delivery plan and should be stated at the start of an engagement, not discovered in week six.

## Business process constraints

- Extend business processes **do not support delegation**.
- Once a business object instance is associated with a business process, **that instance can no longer be
  deleted**.
- Workday **does not lock business object data** after a business process completes.
- Separately, from our own analysis of a precedent corpus (51 `.businessprocess` files, zero `approvalSteps`
  matches): an Extend `.businessprocess` carries a **singular** `approvalStep`, so a variable approver count
  is tenant-side conditional configuration, not file-expressible. Native BP approval pages render
  **view-only**. `CALC/own analysis` — not Workday documentation; attribute accordingly.

## Relationships

An Extend business object targeting a Workday-delivered business object has a **one-way relationship** — for
reporting, the Extend business object must be the data source.

## The three limits that actually change design

**1. Ten security domains per app.** A hard architectural ceiling. Model the security split before building;
it is not something to discover late.

**2. The 100-row page cap means "bulk" has a floor — and WQL is the way around it.** Paged REST returns at
most 100 records per call, so reading 25,000 records is **250 calls, not one**. WQL's ceiling is **1,000,000
rows**, so the same read is one call. Therefore:

> For large reads, use **WQL or a report**, not paged REST.

This is a documented limit driving a consumption decision directly, and it materially changes cost
arithmetic — see the correction note in [../integration-patterns.md](../integration-patterns.md).

**3. The 24-second endpoint and 60-second page timeouts** bound how much a single page can assemble,
independently of cost. A page fanning out to many endpoints is constrained by the clock as well as the bill.

## Genuinely undocumented

- **Number of business objects per app or per tenant** — only the 10-million-instance and 10-domain ceilings
  bind, indirectly.
- **Endpoints per page** — bounded by the 60-second page timeout in practice.
- **TEXT field maximum length for Extend.** Two independent passes have failed to find it. This matters if a
  TEXT field is holding a JSON payload: plan for truncation and test it rather than assuming a ceiling.

## Sources

`doc.workday.com/workday-education/en-us/course-manuals/workday-extend-for-developers/` —
model-component-business-objects-and-security-domains, relationships-between-business-objects,
projects-and-pages. Plus `doc.workday.com/admin-guide/.../custom-objects-and-labels/` for the
custom-objects contrast above (which does **not** govern Extend).
