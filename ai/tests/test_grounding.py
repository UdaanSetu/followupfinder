from ai.inference.grounding import ground_result


def test_removes_invented_contact_organization_and_description():
    text = "Ramesh ke saath meeting kal 3 baje scheduled hai."
    result = {
        "contact": {"name": "Ramesh", "organization": "RK Electricals"},
        "event": {
            "type": "meeting",
            "description": "2BHK flat",
            "amount": None,
            "currency": None,
            "status": "planned",
        },
        "followup": {
            "required": False,
            "action": None,
            "date_expression": None,
        },
    }

    grounded = ground_result(text, result)

    assert grounded["contact"] == {"name": "Ramesh", "organization": None}
    assert grounded["event"]["type"] == "meeting"
    assert grounded["event"]["description"] is None
    assert grounded["event"]["status"] == "planned"
    assert grounded["followup"] == {
        "required": False,
        "action": None,
        "date_expression": None,
    }


def test_preserves_explicit_followup_evidence():
    text = "Rahul ko website quotation bhej diya, Friday ko call karna hai."
    result = {
        "contact": {"name": "Rahul", "organization": "Nova Solutions"},
        "event": {
            "type": "quotation",
            "description": "website quotation",
            "amount": 50000,
            "currency": "INR",
            "status": "completed",
        },
        "followup": {
            "required": True,
            "action": "call",
            "date_expression": "Friday",
        },
    }

    grounded = ground_result(text, result)

    assert grounded["contact"]["organization"] is None
    assert grounded["event"]["description"] == "website quotation"
    assert grounded["followup"] == {
        "required": True,
        "action": "call",
        "date_expression": "Friday",
    }
