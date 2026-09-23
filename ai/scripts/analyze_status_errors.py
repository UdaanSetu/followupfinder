import json
from collections import Counter

errors = Counter()

with open("ai/datasets/lora_full_gpu_results.jsonl", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)

        expected = r.get("expected", {})
        predicted = r.get("prediction", {})

        if not expected or not predicted:
            continue

        e = expected.get("event", {}).get("status")
        p = predicted.get("event", {}).get("status")

        if e != p:
            errors[(e, p)] += 1

print("STATUS ERRORS")
print("-" * 40)

for (expected, predicted), count in errors.most_common():
    print(f"{expected} -> {predicted}: {count}")