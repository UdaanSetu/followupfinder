import json
import random
from pathlib import Path

random.seed(44)

OUT = Path("ai/datasets")
OUT.mkdir(exist_ok=True)

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

# The dangerous nouns that previously became event.type.
TRAPS = [
    ("policy renewal", "quotation"),
    ("admission fee", "payment"),
    ("decoration material", "order"),
    ("washing machine repair", "quotation"),
    ("office renovation", "project"),
    ("contract review", "service"),
    ("insurance claim", "meeting"),
    ("warehouse dispatch", "proposal"),
    ("training package", "order"),
    ("painting material", "delivery"),
    ("software migration", "project"),
    ("client inspection", "visit"),
    ("property purchase", "message"),
    ("wedding video", "email"),
    ("website installation", "service"),
    ("course enrollment", "order"),
]

TYPE_WORDS = {
    "quotation": ["quotation", "quote", "कोटेशन"],
    "payment": ["payment", "पेमेंट"],
    "order": ["order", "ऑर्डर"],
    "project": ["project", "प्रोजेक्ट"],
    "service": ["service", "सेवा"],
    "meeting": ["meeting", "मीटिंग"],
    "proposal": ["proposal", "प्रपोज़ल"],
    "delivery": ["delivery", "डिलीवरी"],
    "visit": ["visit", "विज़िट"],
    "message": ["message", "मैसेज"],
    "email": ["email", "mail", "ईमेल"],
}

STATUS_PHRASES = {
    "planned": [
        "bhejna hai",
        "karna hai",
        "ka plan hai",
        "start karna hai",
        "planned hai",
        "भेजना है",
        "करना है",
        "का प्लान है",
    ],
    "completed": [
        "bhej diya hai",
        "kar diya hai",
        "complete ho gaya hai",
        "sent hai",
        "completed hai",
        "भेज दिया है",
        "कर दिया है",
        "पूरा हो गया है",
    ],
    "pending": [
        "pending hai",
        "ka wait hai",
        "abhi tak nahi hua",
        "waiting hai",
        "पेंडिंग है",
        "का इंतजार है",
        "अभी तक नहीं हुआ",
    ],
    "cancelled": [
        "cancel kar diya hai",
        "cancel ho gaya hai",
        "cancelled hai",
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
    "call": [
        "call karna hai",
        "phone karna hai",
        "फोन करना है",
    ],
    "message": [
        "message karna hai",
        "WhatsApp pe ping karna hai",
        "मैसेज करना है",
    ],
    "email": [
        "email karni hai",
        "mail karni hai",
        "ईमेल भेजनी है",
    ],
}


def make_obj(name, org, event_type, description, amount, status,
             followup, action=None, date=None):

    return {
        "contact": {
            "name": name,
            "organization": org,
        },
        "event": {
            "type": event_type,
            "description": description,
            "amount": amount,
            "currency": "INR" if amount is not None else None,
            "status": status,
        },
        "followup": {
            "required": followup,
            "action": action if followup else None,
            "date_expression": date if followup else None,
        },
    }


def example(text, obj):
    return {
        "messages": [
            {"role": "user", "content": text},
            {
                "role": "assistant",
                "content": json.dumps(
                    obj,
                    ensure_ascii=False
                ),
            },
        ]
    }


examples = []


# ============================================================
# 1. EVENT-TYPE TRAPS
# ============================================================

for description, event_type in TRAPS:
    for name, org in random.sample(CONTACTS, 8):

        type_word = random.choice(TYPE_WORDS[event_type])

        patterns = [
            f"{org} ke {name} ka {description} {type_word} hai.",
            f"{name} ke liye {description} ka {type_word} bhej diya hai.",
            f"{org} ke {name} ke {description} ka {type_word} karna hai.",
            f"{description} ka {type_word} {name} ke liye hai.",
        ]

        text = random.choice(patterns)

        status = random.choice([
            "planned",
            "completed",
            "pending",
            "cancelled",
        ])

        # Replace ending so semantic status is explicit.
        text = text.rstrip(".") + " " + random.choice(
            STATUS_PHRASES[status]
        ) + "."

        examples.append(
            example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    None,
                    status,
                    False,
                ),
            )
        )


# ============================================================
# 2. STATUS MINIMAL PAIRS
# ============================================================

status_templates = [
    ("quotation", "policy renewal"),
    ("payment", "admission fee"),
    ("order", "decoration material"),
    ("meeting", "insurance claim"),
    ("service", "contract review"),
    ("project", "office renovation"),
    ("delivery", "painting material"),
    ("proposal", "warehouse dispatch"),
    ("visit", "client inspection"),
    ("message", "property purchase"),
]

for event_type, description in status_templates:
    for name, org in CONTACTS:

        for status in [
            "planned",
            "completed",
            "pending",
            "unknown",
            "cancelled",
        ]:

            phrase = random.choice(
                STATUS_PHRASES[status]
            )

            type_word = random.choice(
                TYPE_WORDS[event_type]
            )

            text = (
                f"{org} ke {name} ka "
                f"{description} {type_word} "
                f"{phrase}"
            )

            examples.append(
                example(
                    text,
                    make_obj(
                        name,
                        org,
                        event_type,
                        description,
                        None,
                        status,
                        False,
                    ),
                )
            )


# ============================================================
# 3. STATUS + FOLLOW-UP
# ============================================================

for event_type, description in status_templates:

    for name, org in random.sample(CONTACTS, 10):

        status = random.choice([
            "planned",
            "completed",
            "pending",
            "unknown",
            "cancelled",
        ])

        action = random.choice(list(ACTIONS))
        date = random.choice(DATES)

        status_phrase = random.choice(
            STATUS_PHRASES[status]
        )

        type_word = random.choice(
            TYPE_WORDS[event_type]
        )

        action_phrase = random.choice(
            ACTIONS[action]
        )

        text = (
            f"{org} ke {name} ka {description} "
            f"{type_word} {status_phrase} "
            f"{action_phrase} {date}."
        )

        examples.append(
            example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    None,
                    status,
                    True,
                    action,
                    date,
                ),
            )
        )


# ============================================================
# 4. FOLLOW-UP MUST NOT BE INVENTED
# ============================================================

NO_FOLLOWUP = [
    "payment ka status kya hai?",
    "quotation ka kya update hai?",
    "meeting ka wait hai.",
    "order cancel ho gaya hai.",
    "quotation bhej diya hai.",
    "payment karna hai.",
    "delivery mil gayi hai.",
    "appointment cancel ho gayi.",
    "project start karna hai.",
    "client visit ka status kya hai?",
    "email ka update kya hai?",
    "proposal pending hai.",
]

NO_FOLLOWUP_TYPES = [
    ("payment", None),
    ("quotation", None),
    ("meeting", None),
    ("order", None),
    ("quotation", None),
    ("payment", None),
    ("delivery", None),
    ("appointment", None),
    ("project", None),
    ("visit", None),
    ("email", None),
    ("proposal", None),
]

for text, (event_type, _) in zip(
    NO_FOLLOWUP,
    NO_FOLLOWUP_TYPES
):
    examples.append(
        example(
            text,
            make_obj(
                None,
                None,
                event_type,
                None,
                None,
                random.choice([
                    "planned",
                    "completed",
                    "pending",
                    "unknown",
                    "cancelled",
                ]),
                False,
            ),
        )
    )


# ============================================================
# 5. EXPLICIT FOLLOW-UP WITH NO DATE
# ============================================================

NO_DATE = [
    ("Rahul ko quotation bhej diya hai. Call karna hai.", "quotation", "call"),
    ("Neha ka payment pending hai. Message karna hai.", "payment", "message"),
    ("Arjun ke contract review ka update hai. Email karni hai.", "service", "email"),
    ("Priya ka admission payment planned hai. Phone karna hai.", "payment", "call"),
    ("Sonia ka order cancel ho gaya. Message karna hai.", "order", "message"),
    ("Meera ke insurance claim ka status kya hai. Email karni hai.", "meeting", "email"),
]

for text, event_type, action in NO_DATE:
    name = text.split()[0]

    examples.append(
        example(
            text,
            make_obj(
                name,
                None,
                event_type,
                None,
                None,
                "unknown" if "status" in text or "update" in text else (
                    "pending" if "pending" in text else
                    "completed" if "bhej diya" in text else
                    "planned"
                ),
                True,
                action,
                None,
            ),
        )
    )


# ============================================================
# 6. AMOUNT SHOULD NOT CHANGE EVENT TYPE
# ============================================================

amount_cases = [
    ("quotation", "policy renewal", 120000),
    ("payment", "admission fee", 50000),
    ("order", "decoration material", 75000),
    ("proposal", "warehouse dispatch", 150000),
    ("service", "contract review", 50000),
    ("quotation", "washing machine repair", 25000),
]

for event_type, description, amount in amount_cases:
    for name, org in random.sample(CONTACTS, 10):

        type_word = random.choice(
            TYPE_WORDS[event_type]
        )

        amount_text = f"{amount:,}"

        text = (
            f"{org} ke {name} ka {description} "
            f"{type_word} Rs. {amount_text} "
            f"bhej diya hai."
        )

        examples.append(
            example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    amount,
                    "completed",
                    False,
                ),
            )
        )


# ============================================================
# 7. PRESERVE CONTACT + ORGANIZATION
# ============================================================

for name, org in CONTACTS:

    event_type = "quotation"
    description = "website development"

    variants = [
        f"{org} ke {name} ko website development ka quotation bhej diya hai.",
        f"{name} from {org} ka website development quotation sent hai.",
        f"{org} के {name} को website development का quotation भेज दिया है।",
        f"{name} ke liye {org} ka website quotation bhejna hai.",
    ]

    for text in variants:
        status = "completed" if "bhej diya" in text or "sent" in text else "planned"

        examples.append(
            example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    None,
                    status,
                    False,
                ),
            )
        )


# ============================================================
# DEDUPLICATE
# ============================================================

unique = []
seen = set()

for item in examples:
    text = item["messages"][0]["content"]

    if text not in seen:
        seen.add(text)
        unique.append(item)

examples = unique
random.shuffle(examples)


print("ROUND 3 HARD DATASET")
print("=" * 40)
print("Generated:", len(examples))


# Keep approximately 1500.
if len(examples) > 1500:
    examples = examples[:1500]

print("Selected:", len(examples))


path = OUT / "hard_round3.jsonl"

with open(path, "w", encoding="utf-8") as f:
    for item in examples:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("Saved:", path)