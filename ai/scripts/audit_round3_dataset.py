import json
import re
from collections import Counter

FILES = [
    "ai/datasets/train_round3_combined.jsonl",
    "ai/datasets/val_round3.jsonl",
    "ai/datasets/test_round3.jsonl",
]

def norm(text):
    if text is None:
        return ""
    return re.sub(r"\s+", " ", str(text).strip().lower())

def org_explicitly_in_input(text, org):
    if not org:
        return False

    text_n = norm(text)
    org_n = norm(org)

    return org_n in text_n

def description_explicitly_in_input(text, desc):
    if not desc:
        return False

    text_n = norm(text)
    desc_n = norm(desc)

    return desc_n in text_n

for path in FILES:
    try:
        with open(path, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"\nSKIPPED: {path}")
        continue

    org_hidden = []
    desc_unsupported = []
    both = []

    for r in rows:
        text = r.get("input", "")
        assistant = r.get("assistant")

        if isinstance(assistant, str):
            try:
                target = json.loads(assistant)
            except Exception:
                continue
        elif isinstance(assistant, dict):
            target = assistant
        else:
            target = r.get("output", r.get("target", {}))

        if not isinstance(target, dict):
            continue

        contact = target.get("contact", {})
        event = target.get("event", {})

        org = contact.get("organization")
        desc = event.get("description")

        # Problem A:
        # organization is NULL even though the input explicitly contains it.
        org_problem = (
            org is None
            and any(
                candidate
                and norm(candidate) in norm(text)
                for candidate in [
                    "Nova Solutions",
                    "Bright Homes",
                    "ABC Construction",
                    "Sunrise Interiors",
                    "City Care Services",
                    "RK Electricals",
                    "Celebration Studio",
                    "Greenfield Academy",
                    "Vertex Motors",
                    "Orbit Logistics",
                    "Gupta Traders",
                    "Mehta Legal",
                    "LedgerWorks",
                    "SecureLife Insurance",
                    "HomeEase Services",
                ]
            )
        )

        # Problem B:
        # target description does not occur in the user's input.
        desc_problem = (
            desc is not None
            and not description_explicitly_in_input(text, desc)
        )

        if org_problem:
            org_hidden.append(r)

        if desc_problem:
            desc_unsupported.append(r)

        if org_problem and desc_problem:
            both.append(r)

    print("\n" + "=" * 75)
    print(path)
    print("=" * 75)
    print(f"Examples: {len(rows)}")
    print(f"Organization hidden in target: {len(org_hidden)}")
    print(f"Description unsupported by input: {len(desc_unsupported)}")
    print(f"Both problems: {len(both)}")

    print("\nOrganization hidden examples by event type:")
    counter = Counter(
        r.get("assistant", {}).get("event", {}).get("type")
        if isinstance(r.get("assistant"), dict)
        else "unknown"
        for r in org_hidden
    )
    for k, v in counter.most_common():
        print(f"  {k}: {v}")

    print("\nDescription unsupported examples by event type:")
    counter = Counter(
        r.get("assistant", {}).get("event", {}).get("type")
        if isinstance(r.get("assistant"), dict)
        else "unknown"
        for r in desc_unsupported
    )
    for k, v in counter.most_common():
        print(f"  {k}: {v}")

print("\n" + "=" * 75)
print("AUDIT COMPLETE")
print("=" * 75)
