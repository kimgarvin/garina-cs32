# The program works by:
# 1. Parsing the user's craving into keywords
# 2. Expanding vague keywords into related flavor/texture tags
# 3. Scoring each food item based on tag matches
# 4. Returning the best recommendation and a ranked list of foods


food_database = [
    {"name": "French fries",      "tags": ["salty", "crispy", "savory", "greasy"]},
    {"name": "Chocolate cake",    "tags": ["sweet", "rich", "soft", "dessert"]},
    {"name": "Fried chicken",     "tags": ["crispy", "savory", "salty", "hearty", "warm"]},
    {"name": "Caesar salad",      "tags": ["savory", "crunchy", "fresh", "light"]},
    {"name": "Mango sticky rice", "tags": ["sweet", "sticky", "fruity", "soft"]},
    {"name": "Onion rings",       "tags": ["crispy", "salty", "greasy", "savory"]},
    {"name": "Tomato soup",       "tags": ["warm", "comforting", "soft", "light"]},
    {"name": "Mac and cheese",    "tags": ["warm", "comforting", "cheesy", "rich", "hearty"]},
]

# Maps vague craving words to related food tags.
# This helps the program understand more natural user input.
CRAVING_SYNONYMS = {
    "crunchy": ["crispy", "crunchy"],
    "crispy": ["crispy", "crunchy"],
    "salty": ["salty", "savory"],
    "savory": ["savory", "salty"],
    "warm": ["warm", "hearty", "comforting"],
    "comforting": ["comforting", "warm", "soft", "hearty"],
    "sweet": ["sweet", "rich", "fruity"],
    "light": ["light", "fresh"],
    "fresh": ["fresh", "light"],
    "soft": ["soft", "warm"],
    "rich": ["rich", "sweet", "cheesy"],
    "hearty": ["hearty", "warm", "comforting"],
    "greasy": ["greasy", "salty", "savory"],
    "cheesy": ["cheesy", "rich", "comforting"],
    "fruity": ["fruity", "sweet", "fresh"],
}


# --------------------------------------------
# Parsing
# --------------------------------------------

def parse_craving(craving_input):
    """
    Turn a craving string into a cleaned list of keywords.
    Example: 'warm and comforting' -> ['warm', 'comforting']
    """
    text = craving_input.lower()

    # Replace common separators with spaces
    for separator in [",", "&", "/", ";"]:
        text = text.replace(separator, " ")

    # Remove filler words that do not add meaning
    filler_words = {"i", "want", "something", "that", "is", "feels", "like"}
    raw_words = text.split()

    keywords = []
    for word in raw_words:
        if word == "and":
            continue
        if word not in filler_words:
            keywords.append(word)

    return keywords


def expand_keywords(craving_keywords):
    """
    Expand user keywords using the synonym dictionary.
    Example: ['comforting'] -> {'comforting', 'warm', 'soft', 'hearty'}
    """
    expanded = set()

    for keyword in craving_keywords:
        expanded.add(keyword)

        if keyword in CRAVING_SYNONYMS:
            for related_word in CRAVING_SYNONYMS[keyword]:
                expanded.add(related_word)

    return expanded


# --------------------------------------------
# Scoring
# --------------------------------------------

def score_food(food, craving_keywords):
    """
    Score one food item based on overlap between expanded craving words
    and the food's tags.

    Returns:
        score (float)
        matched_tags (set)
    """
    food_tags = set(food["tags"])
    expanded_keywords = expand_keywords(craving_keywords)

    matched_tags = food_tags.intersection(expanded_keywords)

    if not expanded_keywords:
        return 0.0, set()

    score = len(matched_tags) / len(expanded_keywords)
    return score, matched_tags


def rank_foods(craving_input, food_database):
    """
    Return foods ranked by how well they match the craving.
    Each result includes:
        (food name, score, matched tags)
    """
    craving_keywords = parse_craving(craving_input)

    scored_foods = []
    for food in food_database:
        score, matched_tags = score_food(food, craving_keywords)
        scored_foods.append((food["name"], score, matched_tags))

    # Sort by highest score first
    # If scores tie, prefer the food with more matched tags
    scored_foods.sort(key=lambda item: (item[1], len(item[2])), reverse=True)

    return scored_foods


def recommend_food(craving_input, food_database):
    """
    Return the single best food recommendation.
    """
    ranked = rank_foods(craving_input, food_database)
    return ranked[0] if ranked else None


# --------------------------------------------
# Display
# --------------------------------------------

def print_results(craving_input, food_database):
    """
    Print the best recommendation and the full ranking.
    """
    ranked = rank_foods(craving_input, food_database)
    best_match = recommend_food(craving_input, food_database)

    print(f"\nCraving: '{craving_input}'")
    print("=" * 45)

    if best_match is not None:
        name, score, matched_tags = best_match
        print(f"Best match: {name}")
        print(f"Match score: {score:.0%}")
        print(f"Why: matched tags = {sorted(matched_tags)}")
        print("-" * 45)

    print("All ranked results:")
    for name, score, matched_tags in ranked:
        bar = "█" * int(score * 20)
        print(f"{name:<20} {bar:<20} {score:.0%}  matched: {sorted(matched_tags)}")


# --------------------------------------------
# Main program
# --------------------------------------------

def main():
    print("Welcome to the Craving Matcher!")
    user_craving = input("Describe what you're craving: ")
    print_results(user_craving, food_database)


if __name__ == "__main__":
    main()
