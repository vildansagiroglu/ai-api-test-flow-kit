# BOOKER – API Test Flow Prompt Kit (target: Postman + Newman)

Generated from `Restful-Booker.postman_collection.json` with `API_Test_Flow_Kit_Generator.md`.

| | |
| --- | --- |
| Total requests | 8 |
| Resources | 3 (Auth, Booking, Ping) |
| Prompts | 4 (A1, A3, D1, N1) |
| Approx. test cases | 8 |
| Not automated (X) | 0 |

---

## 1. Before you start

- Create an empty Postman collection named **BOOKER – API Test Flows** with collection variables:
  - `baseUrl` = `https://restful-booker.herokuapp.com` (full URL, no leading or trailing spaces)
  - `username` = `admin`, `password` = `password123` (public demo credentials from the API docs)
- Open a **new AI chat for every prompt** below and paste the prompt as it is.
- Suggested order: **A3 → A1 → D1 → N1**. C and F groups do not exist for this API.
- Each prompt adds one folder to the collection. Keep the folders in this order, because flows pass values through collection variables.

**Tool tips**
- A leading or trailing space in `baseUrl` breaks every request.
- Restful-Booker answers `418 I'm a teapot` when the `Accept` header lists several types. Always send exactly `Accept: application/json`.
- The public instance resets its data regularly and other people use it too. Never rely on existing bookings except for read-only checks.
- If a flow stops midway (`--bail`), its cleanup does not run. All test data starts with `RFTEST`, so leftovers are easy to recognise.
- Run with `newman run <collection> --bail` locally or in CI.

## 2. Questions for developers

1. `DELETE /booking/:id` returns **201 Created**. Is this intended? (200 or 204 is expected.)
2. `POST /auth` with wrong credentials returns **200** with `{"reason":"Bad credentials"}` instead of 401. Is this intended?
3. Is `GET /booking/:id` after a delete always 404 (hard delete), or can it be soft-deleted?
4. Is there a rate limit on the public instance that CI runs should respect?

## 3. Group summary

| Group | Topic | Endpoints | ~Cases | Risk |
| --- | --- | --- | --- | --- |
| A1 | Booking read chain (list → id → detail) | 2 | 1 | Low |
| A3 | Health check | 1 | 1 | Low |
| D1 | Booking CRUD flow with auth | 5 | 1 | Medium (writes, self-cleaning) |
| N1 | Negative and security checks (reuses A1/D1 endpoints) | 5 (reused) | 5 | Low (one record, self-cleaning) |
| X | Not automated | 0 | – | – |

## 4. Run plan

- **Smoke:** A3 + A1 (read-only, ~2 s)
- **Regression:** A3 + A1 + D1 + N1 (all folders, on every push and weekly)

---

## 5. Prompts

### A3 – Health check · Low risk · 1 endpoint

```text
GENERAL RULES (apply to every request you create in this chat):
- Target: a Postman collection (v2.1) that will be run with Newman. Add your requests as a new folder of the collection I name in the task.
- Use collection variables such as {{baseUrl}}. Never hardcode the host or a token.
- Headers for every request: "Accept: application/json" (exactly this value, Restful-Booker returns 418 for a multi-value Accept) and, when there is a body, "Content-Type: application/json". Write requests send the token as "Cookie: token={{token}}". If a flow needs a token, call POST /auth with {"username":"{{username}}","password":"{{password}}"} in its first request and save the token with pm.collectionVariables.set.
- Capture values in the request's test script right after it runs, e.g. pm.collectionVariables.set("bookingId", pm.response.json().bookingid). Read them in later requests as {{bookingId}}.
- The request/response shapes I give come from examples and may differ from the real API. RUN the folder once before you finish. If a capture path or field name is wrong, fix it from the real response and run again.
- If a request returns an unexpected status, do NOT weaken the assertion to make it pass. Keep the expected status, keep the request, and report the failure to me (endpoint, status, response body).
- Test data must be recognizable and unique: free text = "RFTEST " + a random 6-character string; generate it in a pre-request script and store it in a collection variable so later requests can assert it. Dates: relative to today (e.g. today +30 days), never fixed past dates.
- Every record created in a folder must be deleted at the end of the same folder (cleanup last, reverse order of creation).
- After a DELETE, call GET by id once and assert 404.
- Assertions per request, each in its own pm.test with a readable name: the documented status code, the key fields I list (exist and, where I give a value, equal it), and response time < 5000 ms.
- Naming: folder "<GROUP> – <topic>", requests "BOOKER | <Resource> | <step>".
- Do not modify or delete folders you did not create in this chat.
- If you cannot run the collection yourself, say so. I will run it with Newman.
- When finished, reply with a table: request | assertions | last run result | notes/failures.

TASK – group A3: health check.
Folder: "A3 – Health check".
1. GET {{baseUrl}}/ping
   Assert: status 201 (documented), body text equals "Created", response time < 5000 ms.
```

### A1 – Booking read chain · Low risk · 2 endpoints

```text
GENERAL RULES (apply to every request you create in this chat):
- Target: a Postman collection (v2.1) that will be run with Newman. Add your requests as a new folder of the collection I name in the task.
- Use collection variables such as {{baseUrl}}. Never hardcode the host or a token.
- Headers for every request: "Accept: application/json" (exactly this value, Restful-Booker returns 418 for a multi-value Accept) and, when there is a body, "Content-Type: application/json". Write requests send the token as "Cookie: token={{token}}". If a flow needs a token, call POST /auth with {"username":"{{username}}","password":"{{password}}"} in its first request and save the token with pm.collectionVariables.set.
- Capture values in the request's test script right after it runs, e.g. pm.collectionVariables.set("bookingId", pm.response.json().bookingid). Read them in later requests as {{bookingId}}.
- The request/response shapes I give come from examples and may differ from the real API. RUN the folder once before you finish. If a capture path or field name is wrong, fix it from the real response and run again.
- If a request returns an unexpected status, do NOT weaken the assertion to make it pass. Keep the expected status, keep the request, and report the failure to me (endpoint, status, response body).
- Test data must be recognizable and unique: free text = "RFTEST " + a random 6-character string; generate it in a pre-request script and store it in a collection variable so later requests can assert it. Dates: relative to today (e.g. today +30 days), never fixed past dates.
- Every record created in a folder must be deleted at the end of the same folder (cleanup last, reverse order of creation).
- After a DELETE, call GET by id once and assert 404.
- Assertions per request, each in its own pm.test with a readable name: the documented status code, the key fields I list (exist and, where I give a value, equal it), and response time < 5000 ms.
- Naming: folder "<GROUP> – <topic>", requests "BOOKER | <Resource> | <step>".
- Do not modify or delete folders you did not create in this chat.
- If you cannot run the collection yourself, say so. I will run it with Newman.
- When finished, reply with a table: request | assertions | last run result | notes/failures.

TASK – group A1: read-only chain on Booking (no writes).
Folder: "A1 – Booking read chain".
1. GET {{baseUrl}}/booking
   Response is a root array (UNVERIFIED): [{"bookingid": 1}, ...].
   Assert: status 200, body is a non-empty array, every item has a numeric "bookingid".
   Capture: the first item's bookingid as readBookingId.
2. GET {{baseUrl}}/booking/{{readBookingId}}
   Assert: status 200; fields exist: firstname, lastname, totalprice, depositpaid, bookingdates.checkin, bookingdates.checkout.
   Note: other users of the public API can delete bookings at any time. If step 2 returns 404, report it as data instability, not as an API bug.
```

### D1 – Booking CRUD flow · Medium risk · 5 endpoints

```text
GENERAL RULES (apply to every request you create in this chat):
- Target: a Postman collection (v2.1) that will be run with Newman. Add your requests as a new folder of the collection I name in the task.
- Use collection variables such as {{baseUrl}}. Never hardcode the host or a token.
- Headers for every request: "Accept: application/json" (exactly this value, Restful-Booker returns 418 for a multi-value Accept) and, when there is a body, "Content-Type: application/json". Write requests send the token as "Cookie: token={{token}}". If a flow needs a token, call POST /auth with {"username":"{{username}}","password":"{{password}}"} in its first request and save the token with pm.collectionVariables.set.
- Capture values in the request's test script right after it runs, e.g. pm.collectionVariables.set("bookingId", pm.response.json().bookingid). Read them in later requests as {{bookingId}}.
- The request/response shapes I give come from examples and may differ from the real API. RUN the folder once before you finish. If a capture path or field name is wrong, fix it from the real response and run again.
- If a request returns an unexpected status, do NOT weaken the assertion to make it pass. Keep the expected status, keep the request, and report the failure to me (endpoint, status, response body).
- Test data must be recognizable and unique: free text = "RFTEST " + a random 6-character string; generate it in a pre-request script and store it in a collection variable so later requests can assert it. Dates: relative to today (e.g. today +30 days), never fixed past dates.
- Every record created in a folder must be deleted at the end of the same folder (cleanup last, reverse order of creation).
- After a DELETE, call GET by id once and assert 404.
- Assertions per request, each in its own pm.test with a readable name: the documented status code, the key fields I list (exist and, where I give a value, equal it), and response time < 5000 ms.
- Naming: folder "<GROUP> – <topic>", requests "BOOKER | <Resource> | <step>".
- Do not modify or delete folders you did not create in this chat.
- If you cannot run the collection yourself, say so. I will run it with Newman.
- When finished, reply with a table: request | assertions | last run result | notes/failures.

TASK – group D1: full CRUD flow on Booking. Dependent flow: if a step fails, the rest is not meaningful (Newman runs with --bail).
Folder: "D1 – Booking CRUD flow".
1. POST {{baseUrl}}/auth  body {"username":"{{username}}","password":"{{password}}"}
   Assert: status 200, "token" exists and is a non-empty string. Capture: token.
2. POST {{baseUrl}}/booking
   Pre-request: firstName = "RFTEST " + random 6 chars, lastName = "RFTEST " + random 6 chars, checkin = today +30 days, checkout = today +33 days (YYYY-MM-DD).
   Body: {"firstname":"{{firstName}}","lastname":"{{lastName}}","totalprice":450,"depositpaid":true,"bookingdates":{"checkin":"{{checkin}}","checkout":"{{checkout}}"},"additionalneeds":"Breakfast"}
   Assert: status 200; bookingid is a number; booking.firstname = firstName; booking.totalprice = 450; booking.bookingdates.checkin = checkin.
   Capture: bookingId.
3. GET {{baseUrl}}/booking/{{bookingId}}
   Assert: status 200; firstname = firstName; lastname = lastName; depositpaid = true.
4. PUT {{baseUrl}}/booking/{{bookingId}}  (Cookie: token={{token}})
   Pre-request: newFirstName = "RFTEST " + random 6 chars.
   Body: same as step 2 but firstname = {{newFirstName}}, totalprice 999, additionalneeds "Late checkout".
   Assert: status 200; firstname = newFirstName; totalprice = 999; additionalneeds = "Late checkout".
5. GET {{baseUrl}}/booking/{{bookingId}}
   Assert: status 200; the PUT values are stored (firstname = newFirstName, totalprice = 999).
6. PATCH {{baseUrl}}/booking/{{bookingId}}  (Cookie: token={{token}})  body {"totalprice":120}
   Assert: status 200; totalprice = 120; firstname still = newFirstName (PATCH must not change other fields).
7. GET {{baseUrl}}/booking?firstname={{newFirstName}}&lastname={{lastName}}
   Note: the value contains a space. URL-encode it (encodeURIComponent in a pre-request script) before putting it in the query string.
   Assert: status 200; the array contains an item with bookingid = bookingId.
8. DELETE {{baseUrl}}/booking/{{bookingId}}  (Cookie: token={{token}})
   Assert: status 201 (documented by the API; report it as a finding because 200/204 is the convention).
9. GET {{baseUrl}}/booking/{{bookingId}}
   Assert: status 404.
```

### N1 – Negative and security checks · Low risk · reuses 5 endpoints

```text
GENERAL RULES (apply to every request you create in this chat):
- Target: a Postman collection (v2.1) that will be run with Newman. Add your requests as a new folder of the collection I name in the task.
- Use collection variables such as {{baseUrl}}. Never hardcode the host or a token.
- Headers for every request: "Accept: application/json" (exactly this value, Restful-Booker returns 418 for a multi-value Accept) and, when there is a body, "Content-Type: application/json". Write requests send the token as "Cookie: token={{token}}". If a flow needs a token, call POST /auth with {"username":"{{username}}","password":"{{password}}"} in its first request and save the token with pm.collectionVariables.set.
- Capture values in the request's test script right after it runs, e.g. pm.collectionVariables.set("bookingId", pm.response.json().bookingid). Read them in later requests as {{bookingId}}.
- The request/response shapes I give come from examples and may differ from the real API. RUN the folder once before you finish. If a capture path or field name is wrong, fix it from the real response and run again.
- If a request returns an unexpected status, do NOT weaken the assertion to make it pass. Keep the expected status, keep the request, and report the failure to me (endpoint, status, response body).
- Test data must be recognizable and unique: free text = "RFTEST " + a random 6-character string; generate it in a pre-request script and store it in a collection variable so later requests can assert it. Dates: relative to today (e.g. today +30 days), never fixed past dates.
- Every record created in a folder must be deleted at the end of the same folder (cleanup last, reverse order of creation).
- After a DELETE, call GET by id once and assert 404.
- Assertions per request, each in its own pm.test with a readable name: the documented status code, the key fields I list (exist and, where I give a value, equal it), and response time < 5000 ms.
- Naming: folder "<GROUP> – <topic>", requests "BOOKER | <Resource> | <step>".
- Do not modify or delete folders you did not create in this chat.
- If you cannot run the collection yourself, say so. I will run it with Newman.
- When finished, reply with a table: request | assertions | last run result | notes/failures.

TASK – group N1: negative and security checks. Use separate variable names (negToken, negBookingId) so this folder does not overwrite D1's variables.
Folder: "N1 – Negative and security checks".
1. POST {{baseUrl}}/auth  body {"username":"{{username}}","password":"wrong-password"}
   Assert: status 200 (current API behaviour, report it as a finding: 401 is the convention); "token" does not exist; reason = "Bad credentials".
2. POST {{baseUrl}}/auth  with the real credentials. Capture: negToken.
3. POST {{baseUrl}}/booking  with an RFTEST booking (same body shape as a normal create). Capture: negBookingId.
4. PUT {{baseUrl}}/booking/{{negBookingId}}  with a valid body and NO Cookie header.
   Assert: status 403.
5. PATCH {{baseUrl}}/booking/{{negBookingId}}  body {"totalprice":1} with Cookie: token=invalid-token.
   Assert: status 403.
6. DELETE {{baseUrl}}/booking/{{negBookingId}}  with Cookie: token=invalid-token.
   Assert: status 403.
7. GET {{baseUrl}}/booking/{{negBookingId}}
   Assert: status 200 and totalprice unchanged, i.e. the rejected PATCH and DELETE did not change or remove the record.
8. GET {{baseUrl}}/booking/999999999
   Assert: status 404.
9. Cleanup: DELETE {{baseUrl}}/booking/{{negBookingId}}  with Cookie: token={{negToken}}. Assert: status 201.
10. GET {{baseUrl}}/booking/{{negBookingId}}  Assert: status 404.
```

---

## 6. Not automated (X)

| Endpoint | Reason |
| --- | --- |
| – | All 8 requests are covered. |

## 7. Appendix – group → endpoints

<details><summary>A1</summary>

- GET /booking
- GET /booking/:id
</details>

<details><summary>A3</summary>

- GET /ping
</details>

<details><summary>D1</summary>

- POST /auth
- POST /booking
- PUT /booking/:id
- PATCH /booking/:id
- DELETE /booking/:id
</details>

<details><summary>N1 (reuses)</summary>

- POST /auth, PUT /booking/:id, PATCH /booking/:id, DELETE /booking/:id, GET /booking/:id
</details>
