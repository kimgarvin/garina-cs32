from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

food_database = [
    {"name": "French Fries",      "tags": ["salty", "crispy", "savory", "greasy"], "emoji": "🍟"},
    {"name": "Chocolate Cake",    "tags": ["sweet", "rich", "soft", "dessert"],    "emoji": "🎂"},
    {"name": "Fried Chicken",     "tags": ["crispy", "savory", "salty", "hearty", "warm"], "emoji": "🍗"},
    {"name": "Caesar Salad",      "tags": ["savory", "crunchy", "fresh", "light"], "emoji": "🥗"},
    {"name": "Mango Sticky Rice", "tags": ["sweet", "sticky", "fruity", "soft"],   "emoji": "🥭"},
    {"name": "Onion Rings",       "tags": ["crispy", "salty", "greasy", "savory"], "emoji": "🧅"},
    {"name": "Tomato Soup",       "tags": ["warm", "comforting", "soft", "light"], "emoji": "🍅"},
    {"name": "Mac and Cheese",    "tags": ["warm", "comforting", "cheesy", "rich", "hearty"], "emoji": "🧀"},
]

CRAVING_SYNONYMS = {
    "crunchy":    ["crispy", "crunchy"],
    "crispy":     ["crispy", "crunchy"],
    "salty":      ["salty", "savory"],
    "savory":     ["savory", "salty"],
    "warm":       ["warm", "hearty", "comforting"],
    "comforting": ["comforting", "warm", "soft", "hearty"],
    "sweet":      ["sweet", "rich", "fruity"],
    "light":      ["light", "fresh"],
    "fresh":      ["fresh", "light"],
    "soft":       ["soft", "warm"],
    "rich":       ["rich", "sweet", "cheesy"],
    "hearty":     ["hearty", "warm", "comforting"],
    "greasy":     ["greasy", "salty", "savory"],
    "cheesy":     ["cheesy", "rich", "comforting"],
    "fruity":     ["fruity", "sweet", "fresh"],
}

def parse_craving(craving_input):
    text = craving_input.lower()
    for sep in [",", "&", "/", ";"]:
        text = text.replace(sep, " ")
    filler_words = {"i", "want", "something", "that", "is", "feels", "like"}
    raw_words = text.split()
    return [w for w in raw_words if w != "and" and w not in filler_words]

def expand_keywords(craving_keywords):
    expanded = set()
    for keyword in craving_keywords:
        expanded.add(keyword)
        if keyword in CRAVING_SYNONYMS:
            expanded.update(CRAVING_SYNONYMS[keyword])
    return expanded

def score_food(food, craving_keywords):
    food_tags = set(food["tags"])
    expanded = expand_keywords(craving_keywords)
    matched = food_tags.intersection(expanded)
    if not expanded:
        return 0.0, set()
    return len(matched) / len(expanded), matched

def rank_foods(craving_input):
    keywords = parse_craving(craving_input)
    scored = []
    for food in food_database:
        score, matched = score_food(food, keywords)
        scored.append({
            "name": food["name"],
            "emoji": food["emoji"],
            "score": round(score * 100),
            "matched_tags": sorted(matched),
            "all_tags": food["tags"],
        })
    scored.sort(key=lambda x: (x["score"], len(x["matched_tags"])), reverse=True)
    return scored

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/match", methods=["POST"])
def match():
    data = request.get_json()
    craving = data.get("craving", "").strip()
    if not craving:
        return jsonify({"error": "Please describe your craving!"}), 400
    results = rank_foods(craving)
    return jsonify({"results": results, "craving": craving})

if __name__ == "__main__":
    app.run(debug=True)
