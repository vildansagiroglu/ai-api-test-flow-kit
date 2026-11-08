# AI API Test Flow Kit

[![API test flows](https://github.com/vildansagiroglu/ai-api-test-flow-kit/actions/workflows/api-flows.yml/badge.svg)](https://github.com/vildansagiroglu/ai-api-test-flow-kit/actions/workflows/api-flows.yml)

A prompt-based method that turns a **Postman collection** into **runnable API test flows** with the help of an AI assistant: read chains, full CRUD flows with auth, and negative/security checks.

I built this method at work with an AI-powered API testing tool (RestFlow) and used it to rebuild **400+ requests** of an enterprise API as automated tests. This repository is a public demo of the same method on the [Restful-Booker](https://restful-booker.herokuapp.com/apidoc/index.html) practice API, with Postman + Newman as the target tool.

## How it works

| Step | Input | Who | Output |
| --- | --- | --- | --- |
| 1. Generate the kit | Postman collection + [generator prompt](kit/API_Test_Flow_Kit_Generator.md) | AI agent (Copilot Agent / Claude Code) | [Project prompt kit](output/BOOKER_Prompt_Kit.md) |
| 2. Create the tests | One kit prompt per chat | AI chat of the target tool | [Test collection](output/BOOKER_API_Test_Flows.postman_collection.json) |
| 3. Run | Test collection | Newman in GitHub Actions | Report on every push and weekly |

**Step 1** is deterministic where it matters: scripts extract every request, assign each one to exactly one group and check that every endpoint appears in a prompt, so nothing is silently skipped.

### Group codes

Every request goes into exactly one group. **The letter is the type of test, ordered by risk. The number is the batch** inside that type.

| Group | What it tests | Risk |
| --- | --- | --- |
| A1, A2… | Read-only chains: list → capture id → get by id (15–20 resources per batch) | None, no data is changed |
| A3 | Single GETs that need no id chain (health check, version, lookups) | None |
| B1 | Search/report endpoints called with an empty filter | None |
| B2 | Read chains between resources (look up a value in one, use it in another) | None |
| C | "Safe update" of shared reference data: write back the current values, then verify | Needs developer approval |
| D1, D2… | Self-contained CRUD flows that create, update and delete their own record (4–6 resources per batch) | Medium, cleans up after itself |
| E1, E2… | Parent → child flows: create the parent, test the child, delete both | Medium |
| F1, F2… | Core business workflows (assign, approve, reject, status changes) | High, needs developer approval and domain review |
| N1 | Negative and security checks: missing or invalid token, wrong credentials, unknown ids | Low |
| X | Not automated, each with a reason (mail, cron, integrations, bulk import) | – |

A large API produces many batches (on the enterprise project: A1–A3, B1–B2, D1–D6, F1–F5…). Restful-Booker has only 8 requests, so it needs just **A3, A1, D1 and N1**: there is no second read batch, and no search, reference-data, parent–child or business-workflow endpoints.

**Run order:** A3 → A1 → D1 → N1. The health check goes first, so if the API is down, the reason for the red run is clear immediately. Then reads, then writes, then negative checks.

**Rules built into every prompt** (learned on the real project): never hardcode hosts or tokens; capture ids from real responses and fix paths after the first run; never weaken an assertion to make a test pass; copy enum values from existing records instead of inventing them; mark test data with an `RFTEST` prefix; delete everything a test creates and verify the delete.

## Results on Restful-Booker

8 requests → 4 prompts (A3, A1, D1, N1) → 22 requests with 60 assertions.

The kit also surfaced API behaviour worth asking developers about:
- `DELETE /booking/:id` returns **201 Created** instead of 200/204.
- `POST /auth` with wrong credentials returns **200** with a reason instead of **401**.
- A multi-value `Accept` header returns **418 I'm a teapot**.

## Run it yourself

```bash
npm install -g newman
newman run output/BOOKER_API_Test_Flows.postman_collection.json --bail
```

Or import the collection into Postman and use the Collection Runner. Re-run the analysis scripts with:

```bash
python3 scripts/extract.py input/Restful-Booker.postman_collection.json
python3 scripts/group.py
python3 scripts/selfcheck.py
```

## Repository structure

```
kit/       generator prompt (tool-agnostic: RestFlow, Postman, …)
input/     source Postman collection
output/    generated prompt kit, endpoint list, grouping, test collection
scripts/   extract → group → self-check
.github/   Newman run on push, pull request and weekly
```

## Author

**Vildan Sağıroğlu** – QA Engineer · [LinkedIn](https://www.linkedin.com/in/vildansagiroglu)
