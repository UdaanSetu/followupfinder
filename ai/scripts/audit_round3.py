import json
from collections import Counter


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


train = load("ai/datasets/train_round3.jsonl")
val = load("ai/datasets/val_round3.jsonl")
test = load("ai/datasets/test_round3.jsonl")


def get_status(item):
    return item["messages"][1]["content"]


def extract(item):
    return json.loads(get_status(item))


def stats(name, data):
    types = Counter()
    statuses = Counter()
    followups = Counter()

    for item in data:
        obj = extract(item)

        types[obj["event"]["type"]] += 1
        statuses[obj["event"]["status"]] += 1
        followups[obj["followup"]["required"]] += 1

    print()
    print("=" * 50)
    print(name)
    print("=" * 50)

    print("\nEvent types:")
    for k, v in sorted(types.items()):
        print(f"{k:15} {v}")

    print("\nStatuses:")
    for k, v in sorted(statuses.items()):
        print(f"{k:15} {v}")

    print("\nFollow-up:")
    for k, v in sorted(followups.items()):
        print(f"{str(k):15} {v}")


stats("TRAIN", train)
stats("VALIDATION", val)
stats("TEST", test)


def inputs(data):
    return {
        item["messages"][0]["content"]
        for item in data
    }


train_inputs = inputs(train)
val_inputs = inputs(val)
test_inputs = inputs(test)

print()
print("=" * 50)
print("SPLIT OVERLAP")
print("=" * 50)

print("Train ∩ Val :", len(train_inputs & val_inputs))
print("Train ∩ Test:", len(train_inputs & test_inputs))
print("Val ∩ Test  :", len(val_inputs & test_inputs))