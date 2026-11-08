# API Test Flow Prompt Kit Generator

Turns any Postman collection into a **project-specific prompt kit**: a Markdown file of ready-to-paste prompts for an AI assistant (RestFlow AI Chat, GitHub Copilot, Claude, …). Each prompt makes the AI create, run and fix a group of API test cases: read chains (list → capture id → get by id), full CRUD flows (create → update → delete → verify) and negative checks.

The method was built at work with RestFlow on an enterprise API with ~380 requests. This repository demonstrates it on the public [Restful-Booker](https://restful-booker.herokuapp.com/apidoc/index.html) API, with Postman + Newman as the target tool.

---

## How to use

**You need:** VS Code + GitHub Copilot Chat in **Agent** mode, or Claude Code. The agent must be able to run scripts in a terminal, because large collections do not fit into the AI's context and must be read with a script.

1. Put these files in one folder:
   - the Postman collection (Export → Collection v2.1)
   - a Swagger/OpenAPI file, if you have one
   - this file
2. Open Copilot Chat in **Agent** mode (or run `claude` in the folder).
3. Copy the **GENERATOR PROMPT** below, fill in `PROJECT INFO`, and send it.
4. The agent writes `<Project>_Prompt_Kit.md`. Follow its "Before you start" section, then paste the prompts into the target tool's AI chat one by one, **opening a new chat for each prompt**.

---

## GENERATOR PROMPT

```text
You are helping a QA engineer turn a Postman collection into a ready-to-use "prompt kit": a Markdown file of self-contained prompts that the engineer pastes, one group at a time, into the AI chat of the target tool. That AI then creates, runs and fixes the test cases. Your job is the analysis and the prompts, not the test cases themselves.

PROJECT INFO (filled in by the engineer):
- Project short name (used in test case names): <e.g. BOOKER>
- Target tool: <RestFlow AI Chat / Postman collection run with Newman / other>
- Postman collection file: <file name>
- Swagger/OpenAPI file (optional): <file name or "none">
- Real base URL for the RestFlow environment: <e.g. https://restful-booker.herokuapp.com>
- Auth: <e.g. "POST /auth with username/password returns a token; write requests send it as Cookie: token=<value>" / Bearer token refreshed manually / basic>
- Test user or test record ids that tests may write to (optional): <ids or "none">
- Known dangerous or off-limits endpoints (optional): <list or "none">

=== STEP 1 – EXTRACT (use a script, do not read the whole collection into context) ===
Write and run a small Python or Node script that walks the collection recursively and saves, for every request:
resource (first folder under the API root), request name, method, path without host, enabled query params, raw body, request-level auth type, the body of the first 2xx example response.
Write endpoints.json and a compact endpoints.txt grouped by resource. One line per request: METHOD path | query keys | body top-level keys | example response top-level keys.
Also print: total request count, count per method, header patterns, collection-level auth, collection variables (baseUrl etc.), collection-level test scripts.
Never copy real tokens, cookies or passwords from the collection into any output, except credentials that the API documentation publishes as public demo credentials.

=== STEP 2 – ANALYZE EACH RESOURCE ===
For each resource, determine:
- which operations exist: GET list, GET by id, POST create, PUT /{id}, PATCH, DELETE, and special actions (e.g. /assign, /approve, /reject)
- the list response shape from the examples (paged {"totalCount","items"} vs root array). Mark it as UNVERIFIED: generated examples are often wrong.
- foreign keys: body fields ending in Id/Ids or named like another resource. Note which resource can provide a valid value (LOOKUP).
- enum-like fields (status, type, category, code values). These must be COPIED from an existing record, never invented.
- danger signals: path or name contains truncate, delete-all, clear, cache, cron, trigger, job, mail, notify, import, bulk, sync, transfer, upload, third-party system names. DELETE on auth/roles. Any GET that changes data (list it separately as a design finding).

=== STEP 3 – GROUP (every request in exactly ONE group) ===
A1/A2… Read-only resources: one case per resource = GET list → capture the first id → GET by id. 15–20 resources per prompt.
A3     Single GETs without an id chain (health, version, lookups).
B1     POST endpoints that only search/list/report. One case each, "empty filter" body.
B2     Read-only chains: lookups by a parent id or by a value taken from another response (e.g. filter a list by a field value read from a record).
C      Shared reference data with only GET + PUT: "safe update" = PUT the record back with its current values, then verify. Requires developer approval.
D1/D2… Self-contained CRUD: POST → GET by id → PUT → GET → PATCH → GET → GET list → DELETE → GET by id. 4–6 resources per prompt.
E1/E2… Parent → child CRUD flows: create the parent(s) in the same case, test the child, delete everything in reverse order.
F1/F2… Core business workflows of the main entity (create → assign/approve/reject/status change → verify → cleanup). Requires developer approval.
N1     Negative and security checks: write requests without auth or with an invalid token, wrong credentials, GET/PUT/DELETE on an id that does not exist, and a check that a rejected delete leaves the record in place.
X      Not automated, with a one-line reason each.
Verify the grouping with the script: print endpoint counts per group and confirm 0 unassigned. N1 reuses endpoints already assigned elsewhere, so do not count it in the total. Keep the mapping script.

=== STEP 4 – WRITE THE PROMPTS ===
Each prompt = the GENERAL RULES block below (verbatim, with <PROJECT> replaced, the auth lines adapted, and the syntax examples translated to the target tool: RestFlow → setVariables steps, {{jsonPath}} / {{randomValue}} / {{now}} helpers, ctx.put in script steps; Postman → pre-request and test scripts, pm.collectionVariables.set, pm.test / pm.expect, pm.response.json(), {{$randomAlphaNumeric}} / {{$isoTimestamp}}) + a blank line + "TASK – group <code>: …".
Each prompt must be self-contained, because the engineer opens a NEW chat for every prompt. Keep each prompt under about 7,000 characters; split groups if needed.
For every endpoint in a task:
- give the path (no host, no placeholder query params)
- give a body template with meaningful values instead of placeholders: text → RFTEST + random, codes → short random, dates → relative to now, FKs → LOOKUP <source endpoint + json path>, enums → COPY <source>
- fields that must hold a real value (ids of users, codes from fixed lists) → LOOKUP or COPY, never RFTEST text
- list the key fields to assert
- for flows, number the steps: auth → lookups → create → capture id → verify → update → verify → list → delete → verify delete
- only use operations that exist in the collection. Never invent actions, statuses or reverse steps that the API does not offer.
Do not put triple backticks inside prompt text.

=== STEP 5 – WRITE THE KIT FILE ===
Write <Project>_Prompt_Kit.md in English, each prompt inside a ```text fenced block:
1. Title + summary (total requests, resources, number of prompts / approx. cases, endpoints not automated)
2. Before you start: new project/collection in the target tool; environment variables (baseUrl as a full URL with no spaces, token or credentials, test ids); a new chat per prompt; suggested order A → B → D → E → N → (after developer approval) C and F; tool tips (see LESSONS)
3. Questions for developers (soft delete?, integration side effects, PUT on reference data allowed?, test user, GETs with side effects)
4. Group summary table: Group | Topic | Endpoints | ~Cases | Risk
5. Run plan (smoke = A+B, regression = all, C separate)
6. Prompts (per group: title, risk, endpoint count, fenced prompt)
7. Not automated (X): Endpoint | Reason
8. Appendix: group → endpoint list

=== STEP 6 – SELF-CHECK BEFORE YOU FINISH ===
- Every non-X endpoint path appears in its group's prompt text (check with the script and print the result).
- Group counts add up to the total request count.
- No private tokens, cookies or passwords appear in the kit.
- No triple backticks inside prompts.
Then give me a short summary: groups, counts, top risks, questions for developers.

=== GENERAL RULES BLOCK (embed verbatim at the top of every prompt) ===
GENERAL RULES (apply to every test case you create in this chat):
- Use environment variables such as {{baseUrl}}. Never hardcode the host or a private token.
- Default headers for every case: "Accept: application/json" and "Content-Type: application/json". Add the auth header the project uses (e.g. "Authorization: Bearer {{token}}" or "Cookie: token={{token}}"); if the token comes from a login endpoint, call it in the first step of the case and capture the token.
- Remove query parameters whose value is a placeholder such as "string". For paged list endpoints send only the page parameters.
- If a captured value goes into a URL path or query string, URL-encode it first in a script step (replace spaces with %20 and "/" with %2F) and ctx.put the result. java.net.URLEncoder may be blocked by the script sandbox.
- Capture ids in a setVariables step right after the request, e.g. {{jsonPath 'response.body' '$[0].bookingid'}} or '$.items[0].id', depending on the real response.
- The request/response shapes I give come from examples and may differ from the real API. RUN every test case once before you finish. If a capture path or field name is wrong, fix it from the real response and run again.
- If a request returns an unexpected 4xx/5xx, do NOT weaken the assertion to make it pass. Keep the expected code, keep the case, and report the failure to me (endpoint, status, response message).
- Values marked COPY: read them from an existing record in an earlier step of the same case instead of inventing them.
- Test data must be recognizable and unique: free text = "RFTEST " + {{randomValue length=6 type='ALPHANUMERIC'}}; short codes = "RF" + {{randomValue length=4 type='ALPHANUMERIC'}}. Dates: relative to now using the {{now}} helper, never fixed past dates.
- Every record created in a case must be deleted at the end of the same case (cleanup last, reverse order of creation).
- After a DELETE, call GET by id once. Observe the first run: if it returns 404, assert 404; if it returns 200 with a delete marker, assert that field; if it returns 200 with no marker, assert 404 anyway and report it to me.
- Dependent flows: stopOnFailure true. Independent read-only checks: stopOnFailure false.
- Assertions per request: the documented success status code (use statusCodeIn when the API documents several), jsonPathExists for the key fields I list, responseTimeMax 5000.
- Naming: "<PROJECT> | <Resource> | <Scenario>". Tag every case with the group code and the resource name.
- Do not modify or delete any existing test case you did not create in this chat.
- If you cannot run the suite yourself, say so. I will run it from the tool (RestFlow UI, Postman runner or Newman).
- When finished, reply with a table: test case | steps | last run result | notes/failures.

=== LESSONS FROM EARLIER PROJECTS (put these as tips in section 2 of the kit) ===
- A leading or trailing space in the baseUrl variable breaks every request ("Illegal character in scheme name").
- RestFlow: if the chat's "run test suite" tool fails, run the suite from the UI (Suites → Run). The cases themselves are fine.
- Postman/Newman: run the collection with `newman run <file> --bail` locally or in CI; flows rely on collection variables, so keep the folder order.
- Auth headers show as ***MASKED*** in run logs. That is expected.
- Example responses can be wrong (array vs paged object). The first run reveals it, and the AI fixes the jsonPath.
- Ids may contain spaces and may not be unique. URL-encode them and report non-unique ids to developers.
- Open a new chat per prompt to keep the context small.
- If a flow stops midway (stopOnFailure), its cleanup does not run. The RFTEST/RF prefix makes leftovers easy to find.
- Some APIs return unusual success codes (e.g. 201 on DELETE). Assert what the API documents, and note it.
- Hand-check any write endpoint that succeeds without auth. That is a security finding.
```

---

## Notes

- **Large collections:** ask the agent for STEP 1–3 first, review the group table, then say "now STEP 4–6".
- **Regrouping:** you can ask "move resource X from D2 to E because it depends on Y". The mapping script makes regeneration easy.
- **Domain knowledge:** business workflows (group F) need the most review. Compare the suggested flows with the real UI flow and correct the order where needed.
