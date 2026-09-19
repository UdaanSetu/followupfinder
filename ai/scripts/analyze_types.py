import json
from collections import Counter

VALID_TYPES = {
    "quotation",
    "payment",
    "meeting",
    "call",
    "message",
    "email",
    "appointment",
    "order",
    "delivery",
    "document",
    "project",
    "service",
    "visit",
    "complaint",
    "proposal",
    "other",
}

errors = Counter()
invalid_predictions = Counter()
valid_wrong = Counter()
skipped = []

with open("ai/datasets/lora_full_gpu_results.jsonl", encoding="utf-8") as f:

    for line_number, line in enumerate(f, 1):

        r = json.loads(line)

        expected = r.get("expected", {})
        prediction = r.get("prediction", {})

        expected_event = expected.get("event")
        predicted_event = prediction.get("event")

        if not isinstance(expected_event, dict):
            skipped.append((line_number, r.get("index")))
            continue

        if not isinstance(predicted_event, dict):
            skipped.append((line_number, r.get("index")))
            continue

        if "type" not in expected_event:
            skipped.append((line_number, r.get("index")))
            continue

        if "type" not in predicted_event:
            skipped.append((line_number, r.get("index")))
            continue

        expected_type = expected_event["type"]
        predicted_type = predicted_event["type"]

        if expected_type != predicted_type:

            errors[(expected_type, predicted_type)] += 1

            if predicted_type not in VALID_TYPES:
                invalid_predictions[predicted_type] += 1
            else:
                valid_wrong[(expected_type, predicted_type)] += 1


print()
print("========================================")
print("EVENT TYPE ERROR ANALYSIS")
print("========================================")

print()
print("Total event.type errors:")
print(sum(errors.values()))

print()
print("INVALID predicted event types:")

if invalid_predictions:

    for value, count in invalid_predictions.most_common():
        print(f"{count:3}  {value!r}")

else:
    print("None")


print()
print("VALID BUT WRONG event types:")

for (expected, predicted), count in valid_wrong.most_common(30):
    print(f"{count:3}  {expected!r} -> {predicted!r}")


print()
print("Skipped malformed records:")
print(len(skipped))

if skipped:
    print(skipped)

print()