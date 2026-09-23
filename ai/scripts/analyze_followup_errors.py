import json

total = 0
expected_true = 0
predicted_missing = 0
predicted_false = 0
predicted_true = 0

with open("ai/datasets/lora_full_gpu_results.jsonl", encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)

        expected = r.get("expected", {})
        predicted = r.get("prediction", {})

        if not expected or not predicted:
            continue

        total += 1

        ef = expected.get("followup", {})
        pf = predicted.get("followup", {})

        if ef.get("required") is True:
            expected_true += 1

            if not pf:
                predicted_missing += 1
            elif pf.get("required") is False:
                predicted_false += 1
            elif pf.get("required") is True:
                predicted_true += 1

print("Total usable:", total)
print("Expected follow-up TRUE:", expected_true)
print("Predicted TRUE:", predicted_true)
print("Predicted FALSE:", predicted_false)
print("Follow-up object missing:", predicted_missing)