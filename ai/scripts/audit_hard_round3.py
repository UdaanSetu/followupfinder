import json
from collections import Counter


PATH = "ai/datasets/hard_round3_v2.jsonl"


with open(PATH, encoding="utf-8") as f:
    data = [json.loads(line) for line in f]


print("HARD DATASET AUDIT")
print("=" * 50)
print("Examples:", len(data))


types = Counter()
statuses = Counter()
followups = Counter()
actions = Counter()

for item in data:
    obj = json.loads(item["messages"][1]["content"])

    types[obj["event"]["type"]] += 1
    statuses[obj["event"]["status"]] += 1
    followups[obj["followup"]["required"]] += 1

    if obj["followup"]["required"]:
        actions[obj["followup"]["action"]] += 1


print("\nEvent types:")
for k, v in sorted(types.items()):
    print(f"{k:15} {v}")


print("\nStatuses:")
for k, v in sorted(statuses.items()):
    print(f"{k:15} {v}")


print("\nFollow-up:")
for k, v in sorted(followups.items()):
    print(f"{str(k):15} {v}")


print("\nActions:")
for k, v in sorted(actions.items()):
    print(f"{str(k):15} {v}")


# Check duplicate inputs
inputs = [
    item["messages"][0]["content"]
    for item in data
]

print("\nDuplicate inputs:", len(inputs) - len(set(inputs)))


# Check malformed JSON
bad = 0

for item in data:
    try:
        json.loads(item["messages"][1]["content"])
    except Exception:
        bad += 1

print("Malformed assistant JSON:", bad)


# Show first 15 examples
print("\n" + "=" * 50)
print("SAMPLE EXAMPLES")
print("=" * 50)

for i, item in enumerate(data[:15]):
    obj = json.loads(item["messages"][1]["content"])

    print("\n---", i, "---")
    print("INPUT:", item["messages"][0]["content"])
    print("TYPE:", obj["event"]["type"])
    print("DESCRIPTION:", obj["event"]["description"])
    print("STATUS:", obj["event"]["status"])
    print("FOLLOWUP:", obj["followup"])