MOCK_EMPLOYEE_WHITELIST = [
    {"name": "Alice Johnson", "email": "alice.johnson@unidesk.com", "role": "employee"},
    {"name": "Bob Martinez", "email": "bob.martinez@unidesk.com", "role": "employee"},
    {"name": "Charlie Nguyen", "email": "charlie.nguyen@unidesk.com", "role": "support_agent"},
    {"name": "Diana Osei", "email": "diana.osei@unidesk.com", "role": "support_agent"},
]


def is_whitelisted(name: str, email: str) -> bool:
    normalized_name = name.strip().lower()
    normalized_email = email.strip().lower()
    return any(
        entry["name"].lower() == normalized_name
        and entry["email"].lower() == normalized_email
        for entry in MOCK_EMPLOYEE_WHITELIST
    )
