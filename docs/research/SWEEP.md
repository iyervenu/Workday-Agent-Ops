# Weekly sweep instructions

Followed by the scheduled "Workday Agent Platform Weekly Sweep" routine. Edit this file to change what the
sweep does — no need to touch the routine itself.

## 1. Load the baseline

Read, in order:

- [README.md](README.md) — conventions; **follow them**, especially `VERIFIED <date>` vs `INFERENCE`
- [workday-agent-platform.md](workday-agent-platform.md)
- [workday-data-cloud.md](workday-data-cloud.md)
- [open-questions.md](open-questions.md) — **the priority**; every item states how to verify it

These hold the current state of knowledge with dates attached. Report only what **changed** since those
dates. Do not restate what is already recorded.

## 2. Sweep these sources

- **`dev.to/workdaydevelopers`** — official Workday developer posts. **Top priority: has the "Lawful Agents"
  series published Part 2 or later?** It is expected to document **Custom Agent Actions** — how a developer
  exposes their own workflow as an agent-callable tool. That is open question #2 and the single most
  consequential unknown.
- **`doc.workday.com/admin-guide`** — the `workday-ai/agents` and `workday-data-cloud` sections
- **`blog.workday.com`** and **`newsroom.workday.com`** — new releases, GA transitions, announcements
- **`github.com/Workday/asor`** — new commits, releases or API additions, especially any **tool-registration**
  or **activity/audit-read** API
- **`community.workday.com`** developer forums — practitioner discussion
- **Independent analysis** — erp.today, diginomica, CIO, Josh Bersin — for critical takes and gaps

Practitioner channels repeatedly carry technical detail (endpoint shapes, auth flows, filter parameters)
that official product pages omit. Weight them accordingly.

## 3. Update the files

Edit surgically — additions and corrections only, no rewrites.

- New verified facts → the relevant file, marked `VERIFIED <today's date>` with its source
- An answered open question → move it out of `open-questions.md` into the right file with a dated marker
- A new unknown → add it to `open-questions.md` **with a concrete verification step**
- Something now contradicted → correct it and note what changed and when. Do not silently overwrite.
- If a source says nothing on a point, record that it is silent. "Not addressed" is a finding.
- **Never fill a gap from your own training data.** If you cannot verify it, say so.

Keep tracked files free of client, tenant or engagement identifiers.

## 4. Commit and report

If anything changed, commit on `main` with a message summarising the findings, and push.

Then email a short digest (under 300 words) to **iyervenu12@gmail.com**, subject
`Workday agent platform — weekly sweep <date>`, covering: what changed, any open question that got
answered, anything that should change current plans, and a one-line "no material change" if that is the
honest answer. Email is best-effort — if it fails, put the digest in your final output instead.

**A quiet week is a valid result.** Do not manufacture findings or pad the digest. "Nothing material
changed; Lawful Agents Part 2 still unpublished" is a perfectly good report.
