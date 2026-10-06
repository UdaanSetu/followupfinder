import json

PATH = "ai/datasets/lora_round3_results.jsonl"

with open(PATH, encoding="utf-8") as f:
    rows = [json.loads(line) for line in f]

errors = [r for r in rows if not r.get("exact_match", False)]

print("=" * 80)
print("ROUND 3 ORGANIZATION + DESCRIPTION CONTEXT AUDIT")
print("=" * 80)
print(f"Total mismatches: {len(errors)}")

for i, r in enumerate(errors, 1):
    exp = r["expected"]
    pred = r["predicted"]

    exp_org = exp.get("contact", {}).get("organization")
    pred_org = pred.get("contact", {}).get("organization")

    exp_desc = exp.get("event", {}).get("description")
    pred_desc = pred.get("event", {}).get("description")

    org_diff = exp_org != pred_org
    desc_diff = exp_desc != pred_desc

    print()
    print("-" * 80)
    print(f"ERROR {i}")

    print("INPUT:")
    print(r.get("input"))

    if org_diff:
        print("\nORGANIZATION:")
        print("  Expected :", repr(exp_org))
        print("  Predicted:", repr(pred_org))

    if desc_diff:
        print("\nDESCRIPTION:")
        print("  Expected :", repr(exp_desc))
        print("  Predicted:", repr(pred_desc))

print()
print("=" * 80)
print("END")
print("=" * 80)
