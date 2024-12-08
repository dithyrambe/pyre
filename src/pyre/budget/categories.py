CATEGORIES = {
    "subscriptions": [
        "phone-internet",
        "leasure",
        "bank-fees",
        "transports",
        "childcare",
    ],
    "home": [
        "energy",
        "condominium",
        "tax",
    ],
    "food": [
        "fridge",
        "extras",
    ],
    "vacations": [
        "mobility",
        "rental",
    ],
    "income": [
        "salary",
        "tax",
    ],
    "health": [
        "medicine",
        "doctor",
    ],
    "savings": [
        "savings",
    ],
    "gifts": [
        "received",
        "given",
    ],
}


LABELS = [
    f"{category}/{subcategory}"
    for category, subcategories in CATEGORIES.items()
    for subcategory in subcategories
]
