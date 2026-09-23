import json
import random
from collections import Counter

random.seed(42)

OUTPUT = "ai/datasets/hard_round3_v2.jsonl"
TARGET = 1200


# ============================================================
# CONTACTS
# ============================================================

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


# ============================================================
# VALID EVENT TYPES
# ============================================================

EVENT_TYPES = [
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


# ============================================================
# TYPE WORDS
# ============================================================

TYPE_WORD = {
    "quotation": "quotation",
    "payment": "payment",
    "meeting": "meeting",
    "call": "call",
    "message": "message",
    "email": "email",
    "appointment": "appointment",
    "order": "order",
    "delivery": "delivery",
    "document": "document",
    "project": "project",
    "service": "service",
    "visit": "visit",
    "complaint": "complaint",
    "proposal": "proposal",
    "other": "matter",
}


# ============================================================
# STATUS PHRASES
# ============================================================

STATUS_PHRASES = {
    "planned": [
        "karna hai",
        "ka plan hai",
        "schedule hai",
        "ki planning hai",
        "start karna hai",
    ],

    "completed": [
        "ho gaya hai",
        "complete ho gaya hai",
        "bhej diya hai",
        "mil gaya hai",
        "kar diya hai",
    ],

    "pending": [
        "pending hai",
        "abhi pending hai",
        "kaam abhi baaki hai",
        "abhi complete nahi hua",
        "iska wait hai",
    ],

    "cancelled": [
        "cancel kar diya hai",
        "cancel ho gaya hai",
        "cancelled hai",
        "cancel kar diya gaya hai",
    ],

    "unknown": [
        "ka kya update hai?",
        "ka status kya hai?",
        "ki situation kya hai?",
        "ka update dekhna hai",
        "ke baare mein pata karna hai",
    ],
}


# ============================================================
# ACTION PHRASES
# ============================================================

ACTIONS = {
    "call": [
        "call karna hai",
        "phone karna hai",
        "call karke confirm karna hai",
    ],

    "message": [
        "message karna hai",
        "WhatsApp pe ping karna hai",
        "message bhejna hai",
    ],

    "email": [
        "email karni hai",
        "mail bhejni hai",
        "email karke confirm karna hai",
    ],
}


# ============================================================
# DATES
# ============================================================

DATES = [
    "aaj",
    "kal",
    "parso",
    "Friday",
    "Saturday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "next week",
    "agle Monday",
    "agle hafte",
    "15/09",
    "20/09",
]


# ============================================================
# DESCRIPTIONS
# ============================================================

DESCRIPTIONS = {
    "quotation": [
        "policy renewal",
        "website development",
        "2BHK flat",
        "washing machine repair",
        "interior work",
        "insurance package",
    ],

    "payment": [
        "admission fee",
        "service payment",
        "project advance",
        "repair payment",
        "pending invoice",
        "consulting fee",
    ],

    "meeting": [
        "insurance claim",
        "project discussion",
        "client discussion",
        "contract review",
        "business discussion",
        "office discussion",
    ],

    "call": [
        "client discussion",
        "payment discussion",
        "project discussion",
        "service discussion",
        "follow-up discussion",
        "business discussion",
    ],

    "message": [
        "property purchase",
        "service update",
        "quotation update",
        "project update",
        "customer update",
        "order update",
    ],

    "email": [
        "quotation email",
        "confirmation email",
        "project update email",
        "payment confirmation email",
        "document email",
        "service confirmation email",
    ],

    "appointment": [
        "site appointment",
        "client appointment",
        "service appointment",
        "demo appointment",
        "consultation appointment",
        "meeting appointment",
    ],

    "order": [
        "decoration material",
        "office furniture",
        "electrical material",
        "wedding package",
        "computer equipment",
        "home appliance",
    ],

    "delivery": [
        "painting material",
        "office equipment",
        "electrical material",
        "wedding items",
        "computer equipment",
        "home supplies",
    ],

    "document": [
        "agreement document",
        "required paperwork",
        "property document",
        "project document",
        "insurance document",
        "legal paperwork",
    ],

    "project": [
        "office renovation",
        "website development",
        "interior renovation",
        "software migration",
        "warehouse setup",
        "home renovation",
    ],

    "service": [
        "contract review",
        "wiring maintenance",
        "AC repair",
        "plumbing work",
        "vehicle servicing",
        "accounting work",
    ],

    "visit": [
        "client inspection",
        "2BHK property",
        "site inspection",
        "office inspection",
        "warehouse inspection",
        "home inspection",
    ],

    "complaint": [
        "service complaint",
        "customer complaint",
        "delivery complaint",
        "product complaint",
        "billing complaint",
        "support complaint",
    ],

    "proposal": [
        "warehouse dispatch",
        "software development",
        "interior renovation",
        "insurance package",
        "logistics service",
        "construction work",
    ],

    "other": [
        "general business matter",
        "client matter",
        "business discussion",
        "general request",
        "miscellaneous work",
        "customer matter",
    ],
}


# ============================================================
# AMOUNTS
# ============================================================

AMOUNTS = [
    (25000, "INR"),
    (50000, "INR"),
    (75000, "INR"),
    (100000, "INR"),
    (150000, "INR"),
]


# ============================================================
# OBJECT CREATOR
# ============================================================

def make_obj(
    name,
    org,
    event_type,
    description,
    status,
    followup=False,
    action=None,
    date=None,
    amount=None,
    currency=None,
):
    return {
        "contact": {
            "name": name,
            "organization": org,
        },

        "event": {
            "type": event_type,
            "description": description,
            "amount": amount,
            "currency": currency,
            "status": status,
        },

        "followup": {
            "required": followup,
            "action": action,
            "date_expression": date,
        },
    }


# ============================================================
# EXAMPLE CREATOR
# ============================================================

def make_example(text, obj):
    return {
        "messages": [
            {
                "role": "user",
                "content": text,
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    obj,
                    ensure_ascii=False,
                ),
            },
        ]
    }


examples = []


# ============================================================
# 1. EVENT TYPE TRAPS
# ============================================================

for event_type in EVENT_TYPES:

    descriptions = DESCRIPTIONS[event_type]

    for description in descriptions:

        for status in [
            "planned",
            "completed",
            "pending",
            "cancelled",
            "unknown",
        ]:

            name, org = random.choice(CONTACTS)

            type_word = TYPE_WORD[event_type]

            status_phrase = random.choice(
                STATUS_PHRASES[status]
            )

            text = (
                f"{org} ke {name} ka "
                f"{description} {type_word} "
                f"{status_phrase}."
            )

            examples.append(
                make_example(
                    text,
                    make_obj(
                        name,
                        org,
                        event_type,
                        description,
                        status,
                    ),
                )
            )


# ============================================================
# 2. STATUS MINIMAL PAIRS
# ============================================================

STATUS_CASES = [
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
    ("appointment", "site appointment"),
    ("email", "confirmation email"),
    ("document", "agreement document"),
    ("complaint", "service complaint"),
    ("call", "client discussion"),
    ("other", "general business matter"),
]


for event_type, description in STATUS_CASES:

    for name, org in CONTACTS:

        for status in [
            "planned",
            "completed",
            "pending",
            "cancelled",
            "unknown",
        ]:

            type_word = TYPE_WORD[event_type]

            status_phrase = random.choice(
                STATUS_PHRASES[status]
            )

            text = (
                f"{org} ke {name} ka "
                f"{description} {type_word} "
                f"{status_phrase}"
            )

            examples.append(
                make_example(
                    text,
                    make_obj(
                        name,
                        org,
                        event_type,
                        description,
                        status,
                    ),
                )
            )


# ============================================================
# 3. STATUS + FOLLOW-UP
# ============================================================

for event_type, description in STATUS_CASES:

    for _ in range(20):

        name, org = random.choice(CONTACTS)

        status = random.choice([
            "planned",
            "completed",
            "pending",
            "cancelled",
            "unknown",
        ])

        action = random.choice(
            list(ACTIONS.keys())
        )

        date = random.choice(DATES)

        type_word = TYPE_WORD[event_type]

        status_phrase = random.choice(
            STATUS_PHRASES[status]
        )

        action_phrase = random.choice(
            ACTIONS[action]
        )

        text = (
            f"{org} ke {name} ka "
            f"{description} {type_word} "
            f"{status_phrase} "
            f"{action_phrase} {date}."
        )

        examples.append(
            make_example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    status,
                    True,
                    action,
                    date,
                ),
            )
        )


# ============================================================
# 4. NO FOLLOW-UP / NO INVENTION
# ============================================================

NO_FOLLOWUP_CASES = [
    ("quotation", "quotation ka kya update hai?", "unknown"),
    ("payment", "payment ka status kya hai?", "unknown"),
    ("meeting", "meeting ka wait hai.", "pending"),
    ("order", "order cancel ho gaya hai.", "cancelled"),
    ("quotation", "quotation bhej diya hai.", "completed"),
    ("payment", "payment karna hai.", "planned"),
    ("delivery", "delivery mil gayi hai.", "completed"),
    ("appointment", "appointment cancel ho gayi.", "cancelled"),
    ("project", "project start karna hai.", "planned"),
    ("visit", "visit ka status kya hai?", "unknown"),
    ("email", "email bhej di hai.", "completed"),
    ("proposal", "proposal pending hai.", "pending"),
    ("call", "call ho gaya hai.", "completed"),
    ("document", "document mil gaya hai.", "completed"),
    ("complaint", "complaint pending hai.", "pending"),
    ("other", "general matter ka update kya hai?", "unknown"),
]


for event_type, sentence, status in NO_FOLLOWUP_CASES:

    for name, org in CONTACTS:

        text = (
            f"{org} ke {name} ke liye "
            f"{sentence}"
        )

        description = None

        examples.append(
            make_example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    status,
                    False,
                ),
            )
        )


# ============================================================
# 5. EXPLICIT FOLLOW-UP WITHOUT DATE
# ============================================================

NO_DATE_CASES = [
    (
        "quotation",
        "policy renewal",
        "completed",
        "call",
        "bhej diya hai",
    ),
    (
        "payment",
        "admission fee",
        "pending",
        "message",
        "pending hai",
    ),
    (
        "service",
        "contract review",
        "completed",
        "email",
        "complete ho gaya hai",
    ),
    (
        "order",
        "decoration material",
        "planned",
        "call",
        "karna hai",
    ),
    (
        "meeting",
        "insurance claim",
        "unknown",
        "message",
        "ka kya update hai?",
    ),
    (
        "proposal",
        "warehouse dispatch",
        "cancelled",
        "email",
        "cancel ho gaya hai",
    ),
    (
        "call",
        "client discussion",
        "completed",
        "message",
        "call ho gaya hai",
    ),
    (
        "document",
        "agreement document",
        "pending",
        "call",
        "pending hai",
    ),
    (
        "complaint",
        "service complaint",
        "pending",
        "message",
        "pending hai",
    ),
    (
        "appointment",
        "site appointment",
        "planned",
        "call",
        "schedule hai",
    ),
    (
        "email",
        "confirmation email",
        "completed",
        "message",
        "bhej di hai",
    ),
    (
        "other",
        "general business matter",
        "unknown",
        "call",
        "ka kya update hai?",
    ),
]


for event_type, description, status, action, status_phrase in NO_DATE_CASES:

    for name, org in CONTACTS:

        type_word = TYPE_WORD[event_type]

        action_phrase = random.choice(
            ACTIONS[action]
        )

        text = (
            f"{org} ke {name} ka "
            f"{description} {type_word} "
            f"{status_phrase} "
            f"{action_phrase}."
        )

        examples.append(
            make_example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    status,
                    True,
                    action,
                    None,
                ),
            )
        )


# ============================================================
# 6. CONTACT + ORGANIZATION PRESERVATION
# ============================================================

for name, org in CONTACTS:

    for event_type in EVENT_TYPES:

        description = random.choice(
            DESCRIPTIONS[event_type]
        )

        text = (
            f"{name} from {org} ka "
            f"{description} {TYPE_WORD[event_type]} "
            f"ka kya update hai?"
        )

        examples.append(
            make_example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    "unknown",
                    False,
                ),
            )
        )


# ============================================================
# 7. AMOUNT + CURRENCY TRAPS
# ============================================================

for event_type in [
    "quotation",
    "payment",
    "order",
    "service",
    "proposal",
]:

    for _ in range(80):

        name, org = random.choice(CONTACTS)

        description = random.choice(
            DESCRIPTIONS[event_type]
        )

        amount, currency = random.choice(
            AMOUNTS
        )

        status = random.choice([
            "planned",
            "completed",
            "pending",
            "cancelled",
            "unknown",
        ])

        status_phrase = random.choice(
            STATUS_PHRASES[status]
        )

        type_word = TYPE_WORD[event_type]

        text = (
            f"{org} ke {name} ka "
            f"{description} {type_word} "
            f"Rs. {amount} ka "
            f"{status_phrase}."
        )

        examples.append(
            make_example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    status,
                    False,
                    None,
                    None,
                    amount,
                    currency,
                ),
            )
        )


# ============================================================
# 8. EXPLICIT FOLLOW-UP + AMOUNT
# ============================================================

for event_type in [
    "quotation",
    "payment",
    "order",
    "proposal",
]:

    for _ in range(40):

        name, org = random.choice(CONTACTS)

        description = random.choice(
            DESCRIPTIONS[event_type]
        )

        amount, currency = random.choice(
            AMOUNTS
        )

        status = random.choice([
            "planned",
            "completed",
            "pending",
            "cancelled",
            "unknown",
        ])

        action = random.choice(
            list(ACTIONS.keys())
        )

        date = random.choice(DATES)

        status_phrase = random.choice(
            STATUS_PHRASES[status]
        )

        action_phrase = random.choice(
            ACTIONS[action]
        )

        text = (
            f"{org} ke {name} ka "
            f"{description} {TYPE_WORD[event_type]} "
            f"Rs. {amount} ka "
            f"{status_phrase} "
            f"{action_phrase} {date}."
        )

        examples.append(
            make_example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    status,
                    True,
                    action,
                    date,
                    amount,
                    currency,
                ),
            )
        )


# ============================================================
# 9. HINDI / HINGLISH HARD CASES
# ============================================================

HARD_LANGUAGE_CASES = [
    ("quotation", "quotation bhej diya hai"),
    ("payment", "payment abhi pending hai"),
    ("meeting", "meeting ka wait hai"),
    ("call", "client ko call karna hai"),
    ("message", "message bhejna hai"),
    ("email", "email bhej di hai"),
    ("appointment", "appointment schedule hai"),
    ("order", "order cancel ho gaya hai"),
    ("delivery", "delivery mil gayi hai"),
    ("document", "document chahiye"),
    ("project", "project start karna hai"),
    ("service", "service complete ho gayi hai"),
    ("visit", "site visit ho gaya"),
    ("complaint", "complaint pending hai"),
    ("proposal", "proposal ka kya update hai"),
    ("other", "general matter ka update kya hai"),
]


for event_type, sentence in HARD_LANGUAGE_CASES:

    for _ in range(25):

        name, org = random.choice(CONTACTS)

        status = random.choice([
            "planned",
            "completed",
            "pending",
            "unknown",
            "cancelled",
        ])

        # Keep sentence semantically aligned with status.
        if "bhej diya" in sentence or "bhej di" in sentence:
            status = "completed"

        elif "pending" in sentence:
            status = "pending"

        elif "wait" in sentence:
            status = "pending"

        elif (
            "karna hai" in sentence
            or "schedule hai" in sentence
        ):
            if "cancel" not in sentence:
                status = "planned"

        elif "cancel" in sentence:
            status = "cancelled"

        elif "mil gayi" in sentence or "complete" in sentence:
            status = "completed"

        elif "kya update" in sentence:
            status = "unknown"

        description = random.choice(
            DESCRIPTIONS[event_type]
        )

        text = (
            f"{org} ke {name} ka "
            f"{description} {sentence}."
        )

        examples.append(
            make_example(
                text,
                make_obj(
                    name,
                    org,
                    event_type,
                    description,
                    status,
                    False,
                ),
            )
        )


# ============================================================
# REMOVE EXACT DUPLICATE INPUTS
# ============================================================

unique_examples = []
seen_inputs = set()

for example in examples:

    user_text = example["messages"][0]["content"]

    if user_text not in seen_inputs:

        seen_inputs.add(user_text)
        unique_examples.append(example)

examples = unique_examples


# ============================================================
# STRATIFIED BALANCED SELECTION
#
# Target:
#   16 event types
#   70 examples/type
#   ~35 follow-up TRUE
#   ~35 follow-up FALSE
#
# 16 * 70 = 1120
#
# Then 80 additional examples are selected while preserving
# the global follow-up balance as closely as possible.
# ============================================================

PER_TYPE = 70
PER_TYPE_FOLLOWUP = 35

selected = []
remaining = []

for event_type in EVENT_TYPES:

    type_true = []
    type_false = []

    for example in examples:

        obj = json.loads(
            example["messages"][1]["content"]
        )

        if obj["event"]["type"] != event_type:
            continue

        if obj["followup"]["required"]:
            type_true.append(example)
        else:
            type_false.append(example)

    random.shuffle(type_true)
    random.shuffle(type_false)

    take_true = min(
        PER_TYPE_FOLLOWUP,
        len(type_true),
    )

    take_false = min(
        PER_TYPE_FOLLOWUP,
        len(type_false),
    )

    selected.extend(
        type_true[:take_true]
    )

    selected.extend(
        type_false[:take_false]
    )

    remaining.extend(
        type_true[take_true:]
    )

    remaining.extend(
        type_false[take_false:]
    )


# ============================================================
# FILL REMAINING SLOTS
#
# We have 1120 base examples if every type has enough TRUE/FALSE.
# Need 80 more.
#
# Maintain the current global TRUE/FALSE ratio as closely as
# possible, targeting 600 TRUE / 600 FALSE overall.
# ============================================================

random.shuffle(remaining)

TRUE_TARGET = TARGET // 2
FALSE_TARGET = TARGET - TRUE_TARGET

current_true = sum(
    json.loads(
        x["messages"][1]["content"]
    )["followup"]["required"]
    for x in selected
)

current_false = len(selected) - current_true


def is_true(example):
    obj = json.loads(
        example["messages"][1]["content"]
    )
    return obj["followup"]["required"] is True


extra_true_needed = max(
    0,
    TRUE_TARGET - current_true
)

extra_false_needed = max(
    0,
    FALSE_TARGET - current_false
)

extra_selected = []

# First satisfy whichever follow-up class is below target.
for want_true, limit in [
    (True, extra_true_needed),
    (False, extra_false_needed),
]:

    if limit <= 0:
        continue

    candidates = [
        x for x in remaining
        if is_true(x) == want_true
    ]

    random.shuffle(candidates)

    chosen = candidates[:limit]

    extra_selected.extend(chosen)

    chosen_ids = {
        x["messages"][0]["content"]
        for x in chosen
    }

    remaining = [
        x for x in remaining
        if x["messages"][0]["content"] not in chosen_ids
    ]


selected.extend(extra_selected)


# ============================================================
# FINAL FILL IF NECESSARY
# ============================================================

if len(selected) < TARGET:

    random.shuffle(remaining)

    selected.extend(
        remaining[:TARGET - len(selected)]
    )


# Safety trim.
selected = selected[:TARGET]

random.shuffle(selected)


# ============================================================
# FINAL VALIDATION
# ============================================================

type_counter = Counter()
status_counter = Counter()
followup_counter = Counter()

duplicate_check = set()

bad_examples = []

for example in selected:

    try:

        user_text = example["messages"][0]["content"]

        if user_text in duplicate_check:
            bad_examples.append(
                ("duplicate", user_text)
            )

        duplicate_check.add(user_text)

        obj = json.loads(
            example["messages"][1]["content"]
        )

        event_type = obj["event"]["type"]
        status = obj["event"]["status"]
        followup = obj["followup"]["required"]

        if event_type not in EVENT_TYPES:
            bad_examples.append(
                ("invalid_event_type", event_type)
            )

        if status not in [
            "planned",
            "completed",
            "pending",
            "cancelled",
            "unknown",
        ]:
            bad_examples.append(
                ("invalid_status", status)
            )

        if not isinstance(followup, bool):
            bad_examples.append(
                ("invalid_followup", followup)
            )

        type_counter[event_type] += 1
        status_counter[status] += 1
        followup_counter[followup] += 1

    except Exception as e:

        bad_examples.append(
            ("malformed", str(e))
        )


# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT,
    "w",
    encoding="utf-8",
) as f:

    for example in selected:

        f.write(
            json.dumps(
                example,
                ensure_ascii=False,
            )
            + "\n"
        )


# ============================================================
# REPORT
# ============================================================

print("ROUND 3 HARD V2")
print("=" * 40)

print("Generated:", len(examples))
print("Selected:", len(selected))
print("Saved:", OUTPUT)

print("\nEvent types:")

for event_type in EVENT_TYPES:

    print(
        f"{event_type:12s}",
        type_counter[event_type]
    )


print("\nStatuses:")

for status in [
    "planned",
    "completed",
    "pending",
    "cancelled",
    "unknown",
]:

    print(
        f"{status:12s}",
        status_counter[status]
    )


print("\nFollow-up:")

print(
    "True :",
    followup_counter[True]
)

print(
    "False:",
    followup_counter[False]
)


print("\nValidation:")

print(
    "Duplicate inputs:",
    len(selected) - len(duplicate_check)
)

print(
    "Bad examples:",
    len(bad_examples)
)


if len(selected) == TARGET and not bad_examples:

    print("\nHARD V2 PASSED")

else:

    print("\nHARD V2 FAILED")

    if bad_examples:

        print(
            "First problems:",
            bad_examples[:10]
        )