import json
import random
from pathlib import Path

random.seed(43)

OUT = Path("ai/datasets")
OUT.mkdir(exist_ok=True)

VALID_TYPES = [
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
]

STATUSES = [
    "planned",
    "completed",
    "pending",
    "cancelled",
    "unknown",
]

CONTACTS = [
    ("Rahul", "Nova Solutions"),
    ("Neha", "Bright Homes"),
    ("Amit", "ABC Construction"),
    ("Anjali", "Sunrise Interiors"),
    ("Vikas", "City Care Services"),
    ("Ramesh", "RK Electricals"),
    ("Sonia", "Celebration Studio"),
    ("Priya", "Greenfield Academy"),
    ("Rohit", "Vertex Motors"),
    ("Pankaj", "Orbit Logistics"),
    ("Gupta ji", "Gupta Traders"),
    ("Arjun", "Mehta Legal"),
    ("Kavita", "LedgerWorks"),
    ("Meera", "SecureLife Insurance"),
    ("Sanjay", "HomeEase Services"),
]

DESCRIPTIONS = [
    "website development",
    "software proposal",
    "2BHK flat",
    "office renovation",
    "interior design",
    "washing machine repair",
    "wiring maintenance",
    "wedding photography",
    "spoken English course",
    "car servicing",
    "warehouse dispatch",
    "retail supply",
    "contract review",
    "policy renewal",
    "painting material",
    "insurance claim",
    "admission fee",
    "training package",
    "decoration material",
    "plumbing work",
]

DATES = [
    "कल",
    "आज",
    "शनिवार",
    "सोमवार",
    "अगले हफ्ते",
    "अगले महीने",
    "2 days later",
    "3 days later",
    "next Monday",
    "Friday",
]

ACTIONS = {
    "call": ["call karna hai", "phone karna hai", "फोन करना है"],
    "message": ["message karna hai", "WhatsApp pe ping karna hai", "मैसेज करना है"],
    "email": ["email karni hai", "mail karni hai", "ईमेल भेजनी है"],
}

# Strong status wording.
STATUS_PHRASES = {
    "planned": [
        "karna hai",
        "karna hai kal",
        "ka plan hai",
        "planned hai",
        "shuru karna hai",
        "bhejna hai",
        "send karna hai",
        "का प्लान है",
        "करना है",
        "भेजना है",
    ],
    "completed": [
        "kar diya hai",
        "bhej diya hai",
        "ho gaya hai",
        "complete ho gaya hai",
        "sent",
        "completed",
        "mil gaya hai",
        "पूरा हो गया है",
        "भेज दिया है",
        "कर दिया है",
    ],
    "pending": [
        "pending hai",
        "ka wait hai",
        "abhi tak nahi hua",
        "abhi pending hai",
        "waiting hai",
        "का इंतजार है",
        "पेंडिंग है",
        "अभी तक नहीं हुआ",
    ],
    "cancelled": [
        "cancel kar diya hai",
        "cancel ho gaya hai",
        "cancelled hai",
        "canceled",
        "कैंसल कर दिया है",
        "कैंसल हो गया है",
    ],
    "unknown": [
        "ka kya update hai?",
        "ka status kya hai?",
        "status dekhna hai",
        "update dekhna hai",
        "ki situation kya hai?",
        "का क्या अपडेट है?",
        "का स्टेटस क्या है?",
        "स्थिति देखनी है",
    ],
}

TYPE_PHRASES = {
    "quotation": [
        "quotation",
        "quote",
        "कोटेशन",
        "quotation ka",
    ],
    "payment": [
        "payment",
        "पेमेंट",
        "payment ka",
    ],
    "meeting": [
        "meeting",
        "मीटिंग",
    ],
    "call": [
        "call",
        "कॉल",
    ],
    "message": [
        "message",
        "मैसेज",
    ],
    "email": [
        "email",
        "mail",
        "ईमेल",
    ],
    "appointment": [
        "appointment",
        "अपॉइंटमेंट",
    ],
    "order": [
        "order",
        "ऑर्डर",
    ],
    "delivery": [
        "delivery",
        "डिलीवरी",
    ],
    "document": [
        "document",
        "documents",
        "डॉक्यूमेंट",
    ],
    "project": [
        "project",
        "प्रोजेक्ट",
    ],
    "service": [
        "service",
        "सेवा",
    ],
    "visit": [
        "visit",
        "विज़िट",
    ],
    "complaint": [
        "complaint",
        "शिकायत",
    ],
    "proposal": [
        "proposal",
        "प्रपोज़ल",
    ],
    "other": [
        "update",
        "work",
        "काम",
    ],
}


def amount_for(description):
    if random.random() < 0.35:
        amount = random.choice([
            5000, 10000, 25000, 50000,
            75000, 100000, 120000, 150000
        ])
        return amount, f"{amount:,}"
    return None, None


def make_example(event_type, status, followup):
    name, org = random.choice(CONTACTS)
    description = random.choice(DESCRIPTIONS)

    amount, amount_text = amount_for(description)

    type_word = random.choice(TYPE_PHRASES[event_type])
    status_word = random.choice(STATUS_PHRASES[status])

    contact_forms = [
        f"{name} ke {description} ka {type_word}",
        f"{org} ke {name} ke {description} ka {type_word}",
        f"{name} ke liye {description} ka {type_word}",
        f"{org} ke {description} ka {type_word}",
    ]

    if status == "unknown":
        base = random.choice([
            f"{name} ke {description} ka {type_word} {status_word}",
            f"{org} ke {description} ka {type_word} {status_word}",
            f"{name} ke {type_word} {status_word}",
        ])
    elif status == "pending":
        base = random.choice([
            f"{name} ka {description} {type_word} {status_word}",
            f"{org} ka {description} {type_word} {status_word}",
            f"{name} ke {type_word} ka wait hai",
        ])
    else:
        base = random.choice([
            f"{name} ke {description} ka {type_word} {status_word}",
            f"{org} ke {name} ke {description} ka {type_word} {status_word}",
            f"{name} ke liye {description} ka {type_word} {status_word}",
        ])

    if amount_text:
        base += f" Rs. {amount_text}"

    follow = {
        "required": False,
        "action": None,
        "date_expression": None,
    }

    if followup:
        action = random.choice(list(ACTIONS.keys()))
        date = random.choice(DATES)
        follow["required"] = True
        follow["action"] = action
        follow["date_expression"] = date

        base += " " + random.choice(ACTIONS[action]) + " " + date

    result = {
        "messages": [
            {
                "role": "user",
                "content": base,
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "contact": {
                        "name": name,
                        "organization": org if random.random() < 0.75 else None,
                    },
                    "event": {
                        "type": event_type,
                        "description": description,
                        "amount": amount,
                        "currency": "INR" if amount is not None else None,
                        "status": status,
                    },
                    "followup": follow,
                }, ensure_ascii=False),
            },
        ]
    }

    return result


examples = []

# 5,000 examples.
for _ in range(5000):
    event_type = random.choice(VALID_TYPES)
    status = random.choice(STATUSES)

    # Balanced follow-up.
    followup = random.random() < 0.5

    examples.append(make_example(
        event_type,
        status,
        followup,
    ))


# Shuffle.
random.shuffle(examples)

# Remove exact duplicates.
unique = []
seen = set()

for item in examples:
    key = item["messages"][0]["content"]
    if key not in seen:
        seen.add(key)
        unique.append(item)

examples = unique

random.shuffle(examples)

# Need enough examples for split.
if len(examples) < 4800:
    raise RuntimeError(
        f"Only {len(examples)} unique examples generated."
    )

train = examples[:4000]
val = examples[4000:4400]
test = examples[4400:4800]


def write_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


write_jsonl(OUT / "train_round3.jsonl", train)
write_jsonl(OUT / "val_round3.jsonl", val)
write_jsonl(OUT / "test_round3.jsonl", test)

print("ROUND 3 DATASET")
print("=" * 40)
print("Unique examples:", len(examples))
print("Train:", len(train))
print("Validation:", len(val))
print("Test:", len(test))
print()
print("Files:")
print(" ai/datasets/train_round3.jsonl")
print(" ai/datasets/val_round3.jsonl")
print(" ai/datasets/test_round3.jsonl")