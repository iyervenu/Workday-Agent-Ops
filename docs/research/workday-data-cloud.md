# Workday Data Cloud

`VERIFIED 2026-10-25`. The **data** layer the agent stack reads from — Workday positions it as opening
*"people and money data to AI agents, analysts, and the platforms you already use."*

## The pieces

Announced 2025-09-16, built on **Apache Iceberg**. Premise: *"no ETL pipelines or duplicate copies,"*
*"no shadow databases or brittle pipelines"* — data queried in place, never moved.

| Component | What it is |
|---|---|
| **Workday Data Lake** | Curated, unified view of Workday HR + finance data blended with third-party sources, with semantic definitions reflecting org structure. |
| **Workday Data Connect** | **Bi-directional, zero-copy** access via Apache Iceberg plus pre-built connectors. |
| **Workday Live Data Query** | Query Workday directly via **SQL over JDBC, and Python** — near-real-time. |
| **Workday Prism** | In-tenant data hub: ingest, transform, analyse. **Tables-based standard as of 2025R1**, visual pipeline experience; also accepts inbound zero-copy queries from external platforms. |

**Choosing between them** (Workday's own guidance):

- **Live Data Query** → transactional reads needing real-time freshness
- **Data Lake** → large-scale analytics where periodic refresh is acceptable
- **Prism ingestion connectors** → when you must *move and transform* into a centralised warehouse; best for
  heavy transforms, multiple joins, large batch, or when a permanent copy is required
- **Zero-Copy Data In** → a live virtual link to source-of-truth; best for real-time visibility and strict
  governance

## Platform status

- **GA** zero-copy federation: **Google BigQuery**, **Salesforce Data 360**, **Snowflake** (Snowflake
  bidirectional is GA)
- **Early Access**: **Databricks** (via Unity Catalog federation), **Amazon SageMaker**
- Zero-copy is **limited to named vendor partners** — explicitly *"not available for general-purpose JDBC
  connections to unsupported tools."*

## The AWS integration (announced 2026-06-02)

Bi-directional zero-copy between AWS data/AI services and Workday's governed HR/finance layer. Three
capabilities in **early access**; GA *"planned for later this year"* (2026), *"with additional capabilities
rolling out through early access programs over the coming quarters."*

- **Amazon Bedrock is the only AWS service named** — *"point AWS data and AI services, like Amazon Bedrock,
  directly at Workday's data layer."* SageMaker, Redshift, Athena, S3, Glue and Lambda are **not** named in
  the announcement, though SageMaker appears as EA in the federation list.
- `INFERENCE:` since **SageMaker Lakehouse is Iceberg-native** — unifying S3 (incl. S3 Tables) with Redshift
  and queryable through Athena or Redshift — the path **Workday → Iceberg → SageMaker Lakehouse →
  Athena/Redshift** is architecturally coherent even though Workday never spells it out.
- **Both directions:** agents built *in* Workday can reach AWS data, and AWS-side agents reach Workday
  payroll/benefits **via the Agent Gateway** with *"the same governance, permissions, and audit controls
  already in place."* Workday claims *"the permission model, business logic, and audit controls travel with
  the data"* — **no technical mechanism is given** (no credential exchange, IAM or OAuth detail).
- **Not mentioned anywhere:** MCP, agent telemetry, audit data, ASOR data.

## Two gaps worth building against

1. **Security-on-read is explicitly the customer's problem.** Workday's words: *"While Workday secures data
   storage within Workday, **you must configure security controls within the partner platform** for data read
   out of Workday."* The moment data lands in AWS, Snowflake or Databricks, row- and column-level security,
   access policy, lineage and retention become the customer's job. That is native AWS work — Lake Formation,
   IAM, Glue catalogue policy — and Workday has no incentive to own it.
2. **Cost governance.** Data Cloud requires a separate SKU and a **mandatory Flex Credits subscription**;
   the Agent Gateway separately **meters every agent interaction**. Combined Workday + AWS cost observability
   for agent and data workloads is unowned.

## Prerequisites and limits

Public Cloud tenant only · separate product SKU/licence · **Flex Credits subscription mandatory** · a contract
with the partner platform required · required domains include *"Data Cloud: Manage Data Lake Access Policies."*
**Not documented:** volume limits, latency, refresh cadence, query throughput, row-level security mechanics.

## Sources

`newsroom.workday.com` (2025-09-16 Data Cloud introduction; 2026-06-02 AWS integration) ·
`doc.workday.com/admin-guide/workday-data-cloud` (setup considerations; zero-copy data in with Snowflake) ·
`workday.com/why-workday/our-technology/data-cloud` · `databricks.com` (Unity Catalog federation) ·
`snowflake.com` (zero-copy integration) · `aws.amazon.com/sagemaker/lakehouse`
