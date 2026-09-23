import json
import random
from pathlib import Path

# ============================================================
# ROUND 2 CORRECTIVE DATASET
# ============================================================
#
# Purpose:
#   Teach the model:
#   1. Do not invent missing dates.
#   2. Do not invent follow-up channels.
#   3. Distinguish explicit action from generic "remind".
#   4. Do not treat pronouns as dates.
#   5. Do not invent currency.
#   6. Preserve completed/pending/cancelled status.
#   7. Handle English, Hindi and Hinglish.
#
# IMPORTANT:
#   - Original Round-1 dataset is NOT modified.
#   - We generate unique user inputs.
#   - Splitting happens AFTER deduplication.
#   - Train/validation/test have zero exact input overlap.
# ============================================================

random.seed(42)

DATA_DIR = Path("ai/datasets")

TRAIN_SIZE = 3200
VALIDATION_SIZE = 400
TEST_SIZE = 400
TOTAL_SIZE = TRAIN_SIZE + VALIDATION_SIZE + TEST_SIZE


# ============================================================
# BUSINESS CONTACTS
# ============================================================

PEOPLE = [
    "Rahul",
    "Amit",
    "Ramesh",
    "Neha",
    "Anjali",
    "Vikas",
    "Rohit",
    "Sonia",
    "Priya",
    "Pankaj",
    "Arjun",
    "Kavita",
    "Meera",
    "Sanjay",
    "Deepak",
    "Nitin",
    "Pooja",
    "Karan",
    "Manish",
    "Sneha",
]

ORGANIZATIONS = [
    "Gupta Traders",
    "Nova Solutions",
    "Bright Homes",
    "ABC Construction",
    "RK Electricals",
    "LedgerWorks",
    "HomeEase Services",
    "Sunrise Interiors",
    "Orbit Logistics",
    "Greenfield Academy",
    "Vertex Motors",
    "SecureLife Insurance",
    "Celebration Studio",
    "City Care Services",
    "Mehta Legal",
]


# ============================================================
# EVENTS
# ============================================================

EVENTS = [
    ("quotation", "website quotation"),
    ("quotation", "construction quotation"),
    ("quotation", "wiring quotation"),
    ("quotation", "interior quotation"),
    ("quotation", "property quotation"),
    ("payment", "construction payment"),
    ("payment", "pending payment"),
    ("payment", "service payment"),
    ("payment", "project payment"),
    ("payment", "invoice payment"),
    ("meeting", "project meeting"),
    ("meeting", "client meeting"),
    ("meeting", "review meeting"),
    ("call", "client call"),
    ("message", "client message"),
    ("email", "project email"),
    ("appointment", "client appointment"),
    ("appointment", "service appointment"),
    ("order", "bulk order"),
    ("order", "material order"),
    ("order", "equipment order"),
    ("delivery", "material delivery"),
    ("delivery", "equipment delivery"),
    ("document", "required document"),
    ("document", "project document"),
    ("document", "verification document"),
    ("project", "website project"),
    ("project", "construction project"),
    ("project", "interior project"),
    ("service", "wiring service"),
    ("service", "repair service"),
    ("service", "installation service"),
    ("visit", "site visit"),
    ("visit", "property visit"),
    ("visit", "inspection visit"),
    ("complaint", "service complaint"),
    ("complaint", "delivery complaint"),
    ("proposal", "business proposal"),
    ("proposal", "project proposal"),
]


# ============================================================
# DATES
# ============================================================

DATES = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday"),
    ("tomorrow", "tomorrow"),
    ("next week", "next week"),
    ("this Friday", "this Friday"),
    ("this Monday", "this Monday"),
    ("next Monday", "next Monday"),
    ("next Friday", "next Friday"),
    ("kal", "kal"),
    ("parso", "parso"),
    ("somvaar", "somvaar"),
    ("mangalvaar", "mangalvaar"),
    ("Friday ko", "Friday ko"),
    ("Monday ko", "Monday ko"),
    ("kal ko", "kal ko"),
]


# ============================================================
# AMOUNTS
# ============================================================

AMOUNTS = [
    (5000, "5000"),
    (10000, "10000"),
    (15000, "15000"),
    (25000, "25000"),
    (50000, "50000"),
    (75000, "75000"),
    (100000, "100000"),
    (150000, "150000"),
    (250000, "250000"),
    (500000, "500000"),
]


# ============================================================
# HELPERS
# ============================================================

def make_example(
    text,
    name=None,
    organization=None,
    event_type=None,
    description=None,
    amount=None,
    currency=None,
    status="unknown",
    followup_required=False,
    action=None,
    date_expression=None,
):
    """
    Creates one training example using our universal schema.
    """

    target = {
        "contact": {
            "name": name,
            "organization": organization,
        },
        "event": {
            "type": event_type,
            "description": description,
            "amount": amount,
            "currency": currency,
            "status": status,
        },
        "followup": {
            "required": followup_required,
            "action": action,
            "date_expression": date_expression,
        },
    }

    return {
        "messages": [
            {
                "role": "user",
                "content": text,
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    target,
                    ensure_ascii=False,
                ),
            },
        ]
    }


def pronoun_for(name):
    """
    We don't actually know a person's gender.
    For dataset variation only, use neutral business-style
    references where possible.
    """

    return random.choice([
        "him",
        "her",
    ])


def hindi_action(action):
    return {
        "call": "call karna hai",
        "message": "message karna hai",
        "email": "email karna hai",
    }[action]


def add(examples, text, **kwargs):
    """
    Add an example only if its user input is unique.
    """

    examples.append(
        make_example(
            text=text,
            **kwargs
        )
    )


# ============================================================
# TEMPLATE POOLS
# ============================================================

EN_MISSING_DATE = [
    "{name} has a pending {desc}. I need to {action} {pronoun}.",
    "I need to {action} {name} about the {desc}.",
    "Please {action} {name} regarding the {desc}.",
    "{name} has a {desc}. I should {action} them.",
    "Need to {action} {name} about the {desc}.",
    "{name}'s {desc} needs attention. I need to {action} them.",
]

HINGLISH_MISSING_DATE = [
    "{name} ka {desc} pending hai, {ha}.",
    "{name} ko {desc} ke liye {ha}.",
    "{name} ke {desc} ke baare mein {ha}.",
    "{name} ka {desc} hai, unko {ha}.",
    "{name} se {desc} ke liye {ha}.",
]

EN_GENERIC_REMIND = [
    "Remind {target} about the {desc} {date}.",
    "Please remind {target} about the {desc} {date}.",
    "I need to remind {target} about the {desc} {date}.",
    "Set a reminder for {target} about the {desc} {date}.",
    "Make sure {target} is reminded about the {desc} {date}.",
]

HINGLISH_GENERIC_REMIND = [
    "{target} ko {date} ko {desc} ke liye yaad dilana hai.",
    "{target} ko {date} ko {desc} ka reminder dena hai.",
    "{target} ko {date} par {desc} ke baare mein remind karna hai.",
    "{target} ke {desc} ko {date} ko yaad dilana hai.",
]

EN_EXPLICIT_ACTION = [
    "Call {name} about the {desc}.",
    "Send {name} a message about the {desc}.",
    "Email {name} regarding the {desc}.",
    "I need to call {name} about the {desc}.",
    "I need to message {name} about the {desc}.",
    "I need to email {name} about the {desc}.",
]

HINGLISH_EXPLICIT_ACTION = [
    "{name} ko {desc} ke liye call karna hai.",
    "{name} ko {desc} ke baare mein message karna hai.",
    "{name} ko {desc} ke regarding email karna hai.",
    "{name} se {desc} ke liye call karna hai.",
    "{name} ko {desc} ka message bhejna hai.",
]

EN_ACTION_DATE = [
    "Call {name} on {date} about the {desc}.",
    "Send {name} a message on {date} about the {desc}.",
    "Email {name} on {date} regarding the {desc}.",
    "I need to call {name} {date} about the {desc}.",
    "I need to message {name} {date} about the {desc}.",
    "I need to email {name} {date} about the {desc}.",
]

HINGLISH_ACTION_DATE = [
    "{name} ko {date} ko {desc} ke liye call karna hai.",
    "{name} ko {date} ko {desc} ka message bhejna hai.",
    "{name} ko {date} ko {desc} ke liye email karna hai.",
    "{date} ko {name} se {desc} ke liye call karna hai.",
]

EN_NO_FOLLOWUP = [
    "{name} received the {desc}. No follow-up is required.",
    "{name}'s {desc} is complete. No follow-up is needed.",
    "No follow-up is needed for {name}'s {desc}.",
    "{name} has completed the {desc}. Nothing else is required.",
]

HINGLISH_NO_FOLLOWUP = [
    "{name} ka {desc} complete ho gaya. Koi follow-up nahi hai.",
    "{name} ka {desc} ho gaya hai, ab follow-up nahi chahiye.",
    "{name} ka {desc} cancel ho gaya. Ab follow-up nahi karna hai.",
    "{name} ke {desc} ke liye koi follow-up required nahi hai.",
]


# ============================================================
# GENERATOR
# ============================================================

def generate_candidates():
    candidates = []

    # --------------------------------------------------------
    # 1. MISSING DATE + EXPLICIT ACTION
    # --------------------------------------------------------

    for name in PEOPLE:
        for event_type, desc in random.sample(EVENTS, min(10, len(EVENTS))):
            for action in ["call", "message", "email"]:

                pronoun = pronoun_for(name)

                # English
                for template in random.sample(
                    EN_MISSING_DATE,
                    min(2, len(EN_MISSING_DATE))
                ):
                    text = template.format(
                        name=name,
                        desc=desc,
                        action=action,
                        pronoun=pronoun,
                    )

                    add(
                        candidates,
                        text,
                        name=name,
                        event_type=event_type,
                        description=desc,
                        status="pending",
                        followup_required=True,
                        action=action,
                        date_expression=None,
                    )

                # Hinglish
                for template in random.sample(
                    HINGLISH_MISSING_DATE,
                    min(2, len(HINGLISH_MISSING_DATE))
                ):
                    text = template.format(
                        name=name,
                        desc=desc,
                        ha=hindi_action(action),
                    )

                    add(
                        candidates,
                        text,
                        name=name,
                        event_type=event_type,
                        description=desc,
                        status="pending",
                        followup_required=True,
                        action=action,
                        date_expression=None,
                    )


    # --------------------------------------------------------
    # 2. GENERIC REMINDER
    #
    # Critical rule:
    # "remind" alone DOES NOT specify call/message/email.
    # --------------------------------------------------------

    for name in PEOPLE:
        for event_type, desc in random.sample(EVENTS, min(8, len(EVENTS))):
            for date_text, date_value in random.sample(
                DATES,
                min(5, len(DATES))
            ):

                target = name

                for template in random.sample(
                    EN_GENERIC_REMIND,
                    min(2, len(EN_GENERIC_REMIND))
                ):
                    text = template.format(
                        target=target,
                        desc=desc,
                        date=date_text,
                    )

                    add(
                        candidates,
                        text,
                        name=name,
                        event_type=event_type,
                        description=desc,
                        status="pending",
                        followup_required=True,
                        action=None,
                        date_expression=date_value,
                    )

                for template in random.sample(
                    HINGLISH_GENERIC_REMIND,
                    min(2, len(HINGLISH_GENERIC_REMIND))
                ):
                    text = template.format(
                        target=target,
                        desc=desc,
                        date=date_text,
                    )

                    add(
                        candidates,
                        text,
                        name=name,
                        event_type=event_type,
                        description=desc,
                        status="pending",
                        followup_required=True,
                        action=None,
                        date_expression=date_value,
                    )


    # --------------------------------------------------------
    # 3. ORGANIZATION + GENERIC REMINDER
    # --------------------------------------------------------

    for organization in ORGANIZATIONS:
        for event_type, desc in random.sample(EVENTS, min(10, len(EVENTS))):
            for date_text, date_value in random.sample(
                DATES,
                min(6, len(DATES))
            ):

                target = organization

                for template in random.sample(
                    EN_GENERIC_REMIND,
                    min(2, len(EN_GENERIC_REMIND))
                ):
                    text = template.format(
                        target=target,
                        desc=desc,
                        date=date_text,
                    )

                    add(
                        candidates,
                        text,
                        organization=organization,
                        event_type=event_type,
                        description=desc,
                        status="pending",
                        followup_required=True,
                        action=None,
                        date_expression=date_value,
                    )

                for template in random.sample(
                    HINGLISH_GENERIC_REMIND,
                    min(2, len(HINGLISH_GENERIC_REMIND))
                ):
                    text = template.format(
                        target=target,
                        desc=desc,
                        date=date_text,
                    )

                    add(
                        candidates,
                        text,
                        organization=organization,
                        event_type=event_type,
                        description=desc,
                        status="pending",
                        followup_required=True,
                        action=None,
                        date_expression=date_value,
                    )


    # --------------------------------------------------------
    # 4. EXPLICIT ACTION WITHOUT DATE
    # --------------------------------------------------------

    for name in PEOPLE:
        for event_type, desc in random.sample(EVENTS, min(12, len(EVENTS))):

            for template in random.sample(
                EN_EXPLICIT_ACTION,
                min(3, len(EN_EXPLICIT_ACTION))
            ):

                if "message" in template:
                    action = "message"
                elif "email" in template:
                    action = "email"
                else:
                    action = "call"

                text = template.format(
                    name=name,
                    desc=desc,
                )

                add(
                    candidates,
                    text,
                    name=name,
                    event_type=event_type,
                    description=desc,
                    status="unknown",
                    followup_required=True,
                    action=action,
                    date_expression=None,
                )

            for template in random.sample(
                HINGLISH_EXPLICIT_ACTION,
                min(2, len(HINGLISH_EXPLICIT_ACTION))
            ):

                if "message" in template:
                    action = "message"
                elif "email" in template:
                    action = "email"
                else:
                    action = "call"

                text = template.format(
                    name=name,
                    desc=desc,
                )

                add(
                    candidates,
                    text,
                    name=name,
                    event_type=event_type,
                    description=desc,
                    status="unknown",
                    followup_required=True,
                    action=action,
                    date_expression=None,
                )


    # --------------------------------------------------------
    # 5. EXPLICIT ACTION + DATE
    # --------------------------------------------------------

    for name in PEOPLE:
        for event_type, desc in random.sample(EVENTS, min(10, len(EVENTS))):

            for action in ["call", "message", "email"]:

                for date_text, date_value in random.sample(
                    DATES,
                    min(5, len(DATES))
                ):

                    if action == "call":
                        template = random.choice([
                            "Call {name} on {date} about the {desc}.",
                            "I need to call {name} {date} about the {desc}.",
                        ])
                    elif action == "message":
                        template = random.choice([
                            "Send {name} a message on {date} about the {desc}.",
                            "I need to message {name} {date} about the {desc}.",
                        ])
                    else:
                        template = random.choice([
                            "Email {name} on {date} regarding the {desc}.",
                            "I need to email {name} {date} about the {desc}.",
                        ])

                    text = template.format(
                        name=name,
                        desc=desc,
                        date=date_text,
                    )

                    add(
                        candidates,
                        text,
                        name=name,
                        event_type=event_type,
                        description=desc,
                        status="unknown",
                        followup_required=True,
                        action=action,
                        date_expression=date_value,
                    )

                    # Hinglish variation
                    template_h = random.choice(HINGLISH_ACTION_DATE)

                    text_h = template_h.format(
                        name=name,
                        desc=desc,
                        date=date_text,
                    )

                    add(
                        candidates,
                        text_h,
                        name=name,
                        event_type=event_type,
                        description=desc,
                        status="unknown",
                        followup_required=True,
                        action=action,
                        date_expression=date_value,
                    )


    # --------------------------------------------------------
    # 6. CURRENCY: EXPLICIT vs NOT EXPLICIT
    # --------------------------------------------------------

    for name in PEOPLE:
        for event_type, desc in [
            ("quotation", "website quotation"),
            ("quotation", "construction quotation"),
            ("payment", "construction payment"),
            ("payment", "pending payment"),
            ("order", "bulk order"),
        ]:

            for amount, amount_text in AMOUNTS:

                # No currency symbol/word
                texts = [
                    f"{name} has a {desc} of {amount_text}.",
                    f"{name} ka {desc} {amount_text} ka hai.",
                    f"{name} ko {amount_text} ka {desc} diya.",
                ]

                for text in texts:
                    add(
                        candidates,
                        text,
                        name=name,
                        event_type=event_type,
                        description=desc,
                        amount=amount,
                        currency=None,
                        status="pending",
                        followup_required=False,
                        action=None,
                        date_expression=None,
                    )

                # Explicit INR
                explicit = [
                    f"{name} has a {desc} of ₹{amount_text}.",
                    f"{name} has a {desc} of INR {amount_text}.",
                    f"{name} ko ₹{amount_text} ka {desc} diya.",
                    f"{name} ka {desc} {amount_text} rupees ka hai.",
                ]

                for text in explicit:
                    add(
                        candidates,
                        text,
                        name=name,
                        event_type=event_type,
                        description=desc,
                        amount=amount,
                        currency="INR",
                        status="pending",
                        followup_required=False,
                        action=None,
                        date_expression=None,
                    )


    # --------------------------------------------------------
    # 7. COMPLETED EVENTS WITHOUT FOLLOW-UP
    # --------------------------------------------------------

    for name in PEOPLE:
        for event_type, desc in random.sample(EVENTS, min(12, len(EVENTS))):

            for template in random.sample(
                EN_NO_FOLLOWUP,
                min(2, len(EN_NO_FOLLOWUP))
            ):

                text = template.format(
                    name=name,
                    desc=desc,
                )

                add(
                    candidates,
                    text,
                    name=name,
                    event_type=event_type,
                    description=desc,
                    status="completed",
                    followup_required=False,
                    action=None,
                    date_expression=None,
                )

            for template in random.sample(
                HINGLISH_NO_FOLLOWUP,
                min(2, len(HINGLISH_NO_FOLLOWUP))
            ):

                status = (
                    "cancelled"
                    if "cancel" in template
                    else "completed"
                )

                text = template.format(
                    name=name,
                    desc=desc,
                )

                add(
                    candidates,
                    text,
                    name=name,
                    event_type=event_type,
                    description=desc,
                    status=status,
                    followup_required=False,
                    action=None,
                    date_expression=None,
                )


    return candidates


# ============================================================
# DEDUPLICATE
# ============================================================

def deduplicate(examples):

    seen = set()
    unique = []

    for example in examples:

        text = example["messages"][0]["content"]

        if text in seen:
            continue

        seen.add(text)
        unique.append(example)

    return unique


# ============================================================
# MAIN
# ============================================================

print("Generating Round-2 candidates...")

candidates = generate_candidates()

print("Candidates generated:", len(candidates))

unique_examples = deduplicate(candidates)

print("Unique examples:", len(unique_examples))
print(
    "Duplicate candidates removed:",
    len(candidates) - len(unique_examples)
)


if len(unique_examples) < TOTAL_SIZE:
    raise RuntimeError(
        f"Only {len(unique_examples)} unique examples generated. "
        f"Need at least {TOTAL_SIZE}."
    )


# Take exactly 4000 unique examples.
random.shuffle(unique_examples)

selected = unique_examples[:TOTAL_SIZE]


# ------------------------------------------------------------
# Split AFTER deduplication
# ------------------------------------------------------------

train = selected[:TRAIN_SIZE]

validation = selected[
    TRAIN_SIZE:
    TRAIN_SIZE + VALIDATION_SIZE
]

test = selected[
    TRAIN_SIZE + VALIDATION_SIZE:
    TOTAL_SIZE
]


# ============================================================
# WRITE JSONL
# ============================================================

def write_jsonl(path, rows):

    with open(path, "w", encoding="utf-8") as f:

        for row in rows:

            f.write(
                json.dumps(
                    row,
                    ensure_ascii=False
                ) + "\n"
            )


write_jsonl(
    DATA_DIR / "round2_train.jsonl",
    train
)

write_jsonl(
    DATA_DIR / "round2_validation.jsonl",
    validation
)

write_jsonl(
    DATA_DIR / "round2_test.jsonl",
    test
)


# ============================================================
# FINAL VERIFICATION
# ============================================================

def inputs(rows):
    return {
        row["messages"][0]["content"]
        for row in rows
    }


train_inputs = inputs(train)
validation_inputs = inputs(validation)
test_inputs = inputs(test)

print()
print("=" * 60)
print("ROUND-2 DATASET COMPLETE")
print("=" * 60)

print("Train:", len(train))
print("Validation:", len(validation))
print("Test:", len(test))
print("Total:", len(train) + len(validation) + len(test))

print()
print("Unique train inputs:", len(train_inputs))
print("Unique validation inputs:", len(validation_inputs))
print("Unique test inputs:", len(test_inputs))

print()
print("Train ∩ Validation:", len(train_inputs & validation_inputs))
print("Train ∩ Test:", len(train_inputs & test_inputs))
print("Validation ∩ Test:", len(validation_inputs & test_inputs))

print()
print("Files:")
print("  ai/datasets/round2_train.jsonl")
print("  ai/datasets/round2_validation.jsonl")
print("  ai/datasets/round2_test.jsonl")

print()
print("No original Round-1 dataset was modified.")
