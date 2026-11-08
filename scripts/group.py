"""STEP 2-3 - assign every request to exactly one group and verify coverage."""
import json
rows = json.load(open("output/endpoints.json"))
GROUPS = {
    "A1": [("GET", "/booking"), ("GET", "/booking/:id")],
    "A3": [("GET", "/ping")],
    "D1": [("POST", "/auth"), ("POST", "/booking"), ("PUT", "/booking/:id"),
           ("PATCH", "/booking/:id"), ("DELETE", "/booking/:id")],
    "X":  [],
}
# N1 reuses endpoints from A1/D1 and is not counted in the total
N1_REUSES = [("POST", "/auth"), ("PUT", "/booking/:id"), ("PATCH", "/booking/:id"),
             ("DELETE", "/booking/:id"), ("GET", "/booking/:id")]
assigned = {}
for g, eps in GROUPS.items():
    for ep in eps:
        assert ep not in assigned, f"{ep} in two groups"
        assigned[ep] = g
all_eps = [(r["method"], r["path"]) for r in rows]
unassigned = [e for e in all_eps if e not in assigned]
for g, eps in GROUPS.items():
    print(f"{g}: {len(eps)} endpoints")
print("N1 (reuse, not counted):", len(N1_REUSES))
print("total assigned:", sum(len(v) for v in GROUPS.values()), "/", len(all_eps))
print("unassigned:", unassigned)
json.dump({g: [" ".join(e) for e in eps] for g, eps in GROUPS.items()} | {"N1": [" ".join(e) for e in N1_REUSES]},
          open("output/groups.json", "w"), indent=2)
