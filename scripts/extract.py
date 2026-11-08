"""STEP 1 - walk a Postman v2.1 collection and list every request compactly."""
import json, sys
from collections import Counter

def walk(items, folder=None):
    for it in items:
        if "item" in it:
            yield from walk(it["item"], folder or it["name"])
        else:
            yield folder, it

def main(path):
    col = json.load(open(path))
    rows = []
    for folder, it in walk(col["item"]):
        r = it["request"]; url = r["url"]
        p = "/" + "/".join(url.get("path", []))
        q = [x["key"] for x in url.get("query", []) if not x.get("disabled")]
        body = r.get("body", {}).get("raw")
        bkeys = list(json.loads(body).keys()) if body else []
        ex = next((x for x in it.get("response", []) if 200 <= x.get("code", 0) < 300), None)
        ekeys, ecode = [], None
        if ex:
            ecode = ex["code"]
            try:
                b = json.loads(ex["body"])
                ekeys = list(b[0].keys()) + ["(array)"] if isinstance(b, list) else list(b.keys())
            except Exception:
                ekeys = ["(text)"]
        hdr = [h["key"] for h in r.get("header", [])]
        rows.append(dict(resource=folder, name=it["name"], method=r["method"], path=p, query=q,
                         body_keys=bkeys, example_code=ecode, example_keys=ekeys, headers=hdr,
                         body=body))
    json.dump(rows, open("output/endpoints.json", "w"), indent=2)
    with open("output/endpoints.txt", "w") as f:
        for res in dict.fromkeys(r["resource"] for r in rows):
            f.write(f"[{res}]\n")
            for r in rows:
                if r["resource"] == res:
                    f.write(f"  {r['method']} {r['path']} | q={r['query']} | body={r['body_keys']} | "
                            f"{r['example_code']} {r['example_keys']}\n")
    print("total requests:", len(rows))
    print("per method:", dict(Counter(r["method"] for r in rows)))
    print("header patterns:", dict(Counter(tuple(r["headers"]) for r in rows)))
    print("collection auth:", col.get("auth"))
    print("collection variables:", [v["key"] for v in col.get("variable", [])])
    print("collection test scripts:", bool(col.get("event")))

if __name__ == "__main__":
    main(sys.argv[1])
