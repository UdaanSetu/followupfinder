import json

targets = {
    ("planned", "pending"),
    ("completed", "pending"),
    ("unknown", "pending"),
    ("cancelled", "pending"),
}

shown = {key: 0 for key in targets}
limit = 5

with open("ai/datasets/lora_full_gpu_results.jsonl", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)

        expected = r.get("expected", {})
        predicted = r.get("prediction", {})

        if not expected or not predicted:
            continue

        e = expected.get("event", {}).get("status")
        p = predicted.get("event", {}).get("status")

        key = (e, p)

        if key in targets and shown[key] < limit:
            print("\n" + "=" * 70)
            print("ERROR:", e, "->", p)
            print("INPUT:")
            print(r.get("input", [{}])[0].get("content", ""))
            print("\nEXPECTED:")
            print(json.dumps(expected, ensure_ascii=False, indent=2))
            print("\nPREDICTED:")
            print(json.dumps(predicted, ensure_ascii=False, indent=2))

            shown[key] += 1

print("\n\nSUMMARY")
for key, count in shown.items():
    print(key, "examples shown:", count)