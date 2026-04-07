def parse_craving(craving_input):
    """Turn a craving string into a list of flavor keywords."""
    # Simple approach: split on spaces and common separators, lowercase everything
    separators = [" and ", ", ", " & ", " "]
    keywords = [craving_input.lower()]
    for sep in separators:
        new_keywords = []
        for kw in keywords:
            new_keywords.extend(kw.split(sep))
        keywords = new_keywords
    return [kw.strip() for kw in keywords if kw.strip()]


def score_food(food, craving_keywords):
    """Score a food item based on how many craving keywords match its tags."""
    food_tags = set(food["tags"])
    craving_set = set(craving_keywords)
    matches = food_tags.intersection(craving_set)
    score = len(matches) / len(craving_set) if craving_set else 0
    return score


def rank_foods(craving_input, food_database):
    """Return foods ranked by how well they match the craving."""
    craving_keywords = parse_craving(craving_input)
    print(f"Craving keywords: {craving_keywords}\n")

    scored = []
    for food in food_database:
        score = score_food(food, craving_keywords)
        scored.append((food["name"], score))

    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


# --- Sample run ---
craving = "salty and crispy"

food_database = [
    {"name": "French fries",      "tags": ["salty", "crispy", "savory"]},
    {"name": "Chocolate cake",    "tags": ["sweet", "rich", "soft"]},
    {"name": "Fried chicken",     "tags": ["crispy", "savory", "salty", "hearty"]},
    {"name": "Caesar salad",      "tags": ["savory", "crunchy", "fresh"]},
    {"name": "Mango sticky rice", "tags": ["sweet", "sticky", "fruity"]},
    {"name": "Onion rings",       "tags": ["crispy", "salty", "greasy"]},
]

results = rank_foods(craving, food_database)

print(f"Results for craving: '{craving}'")
print("-" * 35)
for name, score in results:
    bar = "█" * int(score * 10)
    print(f"{name:<22} {bar:<10} {score:.0%}")
