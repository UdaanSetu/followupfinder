import json
from collections import Counter

PATH = "ai/datasets/lora_round3_results.jsonl"

with open(PATH, encoding="utf-8") as f:
    rows = [json.loads(line) for line in f]

errors = [r for r in rows if not r.get("exact_match", False)]

categories = Counter()
genuine = []

def get(d, *keys):
    for k in keys:
        d = d.get(k, {}) if isinstance(d, dict) else {}
    return d if not isinstance(d, dict) else d

for r in errors:
    expected = r["expected"]
    predicted = r["predicted"]

    exp_contact = expected.get("contact", {})
    pred_contact = predicted.get("contact", {})
    exp_event = expected.get("event", {})
    pred_event = predicted.get("event", {})

    org_diff = (
        exp_contact.get("organization")
        != pred_contact.get("organization")
    )

    desc_diff = (
        exp_event.get("description")
        != pred_event.get("description")
    )

    # Check whether other important fields differ.
    important_diffs = []

    fields = [
        ("contact.name", exp_contact.get("name"), pred_contact.get("name")),
        ("event.type", exp_event.get("type"), pred_event.get("type")),
        ("event.amount", exp_event.get("amount"), pred_event.get("amount")),
        ("event.currency", exp_event.get("currency"), pred_event.get("currency")),
        ("event.status", exp_event.get("status"), pred_event.get("status")),
        ("followup.required",
         expected.get("followup", {}).get("required"),
         predicted.get("followup", {}).get("required")),
        ("followup.action",
         expected.get("followup", {}).get("action"),
         predicted.get("followup", {}).get("action")),
        ("followup.date_expression",
         expected.get("followup", {}).get("date_expression"),
         predicted.get("followup", {}).get("date_expression")),
    ]

    for name, exp, pred in fields:
        if exp != pred:
            important_diffs.append(name)

    if not important_diffs and org_diff and desc_diff:
        category = "ORG + DESCRIPTION ONLY"
    elif not important_diffs and org_diff:
        category = "ORGANIZATION ONLY"
    elif not important_diffs and desc_diff:
        category = "DESCRIPTION ONLY"
    else:
        category = "GENUINE / OTHER"

    categories[category] += 1

    if category == "GENUINE / OTHER":
        genuine.append(r)

print("=" * 70)
print("ROUND 3 ERROR ANALYSIS")
print("=" * 70)

print(f"Total examples : {len(rows)}")
print(f"Exact matches  : {len(rows) - len(errors)}")
print(f"Mismatches     : {len(errors)}")
print()

print("CATEGORIES")
print("-" * 70)

for category, count in categories.most_common():
    print(f"{category:25} {count:3}")

print()
print("=" * 70)
print("GENUINE / OTHER ERRORS")
print("=" * 70)

print(f"Count: {len(genuine)}")
print()

for i, r in enumerate(genuine, 1):
    print("-" * 70)
    print(f"ERROR {i}")
    print("INPUT:")
    print(r.get("input"))

    print("\nEXPECTED:")
    print(json.dumps(
        r.get("expected"),
        ensure_ascii=False,
        indent=2
    ))

    print("\nPREDICTED:")
    print(json.dumps(
        r.get("predicted"),
        ensure_ascii=False,
        indent=2
    ))

print()
print("=" * 70)
print("END")
print("=" * 70)
