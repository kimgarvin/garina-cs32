from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ── Data ──────────────────────────────────────────────────────────────────────

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

# ── Logic ─────────────────────────────────────────────────────────────────────

def parse_craving(craving_input):
    text = craving_input.lower()
    for sep in [",", "&", "/", ";"]:
        text = text.replace(sep, " ")
    filler_words = {"i", "want", "something", "that", "is", "feels", "like"}
    return [w for w in text.split() if w != "and" and w not in filler_words]

def expand_keywords(keywords):
    expanded = set()
    for kw in keywords:
        expanded.add(kw)
        expanded.update(CRAVING_SYNONYMS.get(kw, []))
    return expanded

def score_food(food, keywords):
    food_tags = set(food["tags"])
    expanded  = expand_keywords(keywords)
    matched   = food_tags & expanded
    if not expanded:
        return 0.0, set()
    return len(matched) / len(expanded), matched

def rank_foods(craving_input):
    keywords = parse_craving(craving_input)
    scored = []
    for food in food_database:
        score, matched = score_food(food, keywords)
        scored.append({
            "name":         food["name"],
            "emoji":        food["emoji"],
            "score":        round(score * 100),
            "matched_tags": sorted(matched),
            "all_tags":     food["tags"],
        })
    scored.sort(key=lambda x: (x["score"], len(x["matched_tags"])), reverse=True)
    return scored

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/match", methods=["POST"])
def match():
    data    = request.get_json()
    craving = data.get("craving", "").strip()
    if not craving:
        return jsonify({"error": "Please describe your craving!"}), 400
    return jsonify({"results": rank_foods(craving), "craving": craving})

# ── Template ──────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Craving Matcher</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
  <style>
    :root {
      --cream:  #f5efe6;
      --warm:   #e8d5b0;
      --rust:   #c0522a;
      --ember:  #e87d3e;
      --bark:   #3d2b1f;
      --ink:    #1e1410;
      --muted:  #9a8070;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'DM Sans', sans-serif;
      background-color: var(--cream);
      color: var(--ink);
      min-height: 100vh;
      overflow-x: hidden;
    }
    body::before {
      content: '';
      position: fixed; inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
      pointer-events: none; z-index: 0;
    }
    header {
      position: relative;
      padding: 3rem 2rem 2.5rem;
      text-align: center;
      border-bottom: 1.5px solid var(--warm);
    }
    .header-tag {
      font-family: 'DM Mono', monospace;
      font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase;
      color: var(--rust); margin-bottom: 0.75rem;
    }
    h1 {
      font-family: 'Playfair Display', serif;
      font-size: clamp(2.4rem, 6vw, 4rem);
      font-weight: 700; line-height: 1.05;
      color: var(--bark); letter-spacing: -0.02em;
    }
    h1 span { font-style: italic; font-weight: 400; color: var(--rust); }
    .header-sub { margin-top: 0.6rem; font-size: 0.95rem; color: var(--muted); font-weight: 300; }
    main {
      max-width: 780px; margin: 0 auto;
      padding: 2.5rem 1.5rem 5rem;
      position: relative; z-index: 1;
    }
    .input-section { margin-bottom: 2.5rem; }
    .input-label {
      display: block; font-family: 'DM Mono', monospace;
      font-size: 0.72rem; letter-spacing: 0.15em; text-transform: uppercase;
      color: var(--muted); margin-bottom: 0.6rem;
    }
    .input-row { display: flex; gap: 0.75rem; align-items: stretch; }
    #craving-input {
      flex: 1; padding: 0.95rem 1.2rem;
      font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.15rem;
      color: var(--bark); background: #fff;
      border: 1.5px solid var(--warm); border-radius: 6px; outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    #craving-input::placeholder { color: #c4b09a; }
    #craving-input:focus {
      border-color: var(--rust);
      box-shadow: 0 0 0 3px rgba(192,82,42,0.1);
    }
    #match-btn {
      padding: 0 1.6rem; background: var(--rust); color: #fff; border: none;
      border-radius: 6px; font-family: 'DM Mono', monospace;
      font-size: 0.78rem; letter-spacing: 0.1em; text-transform: uppercase;
      cursor: pointer; transition: background 0.2s, transform 0.1s; white-space: nowrap;
    }
    #match-btn:hover  { background: var(--ember); }
    #match-btn:active { transform: scale(0.97); }
    .chips { display: flex; flex-wrap: wrap; gap: 0.45rem; margin-top: 0.85rem; }
    .chip {
      padding: 0.3rem 0.75rem; background: var(--warm); color: var(--bark);
      border-radius: 999px; font-size: 0.8rem; cursor: pointer;
      transition: background 0.15s, color 0.15s; user-select: none;
    }
    .chip:hover { background: var(--rust); color: #fff; }
    #results { display: none; }
    .results-heading {
      font-family: 'Playfair Display', serif; font-size: 1rem; font-style: italic;
      color: var(--muted); margin-bottom: 1.25rem;
      padding-bottom: 0.75rem; border-bottom: 1px solid var(--warm);
    }
    .results-heading strong { font-style: normal; font-weight: 700; color: var(--bark); }
    .best-card {
      background: var(--bark); color: var(--cream); border-radius: 10px;
      padding: 1.75rem 2rem; margin-bottom: 1.5rem;
      display: flex; align-items: center; gap: 1.5rem;
      animation: slideUp 0.4s ease both;
    }
    .best-emoji { font-size: 3.5rem; line-height: 1; flex-shrink: 0; }
    .best-info  { flex: 1; }
    .best-label {
      font-family: 'DM Mono', monospace; font-size: 0.65rem;
      letter-spacing: 0.2em; text-transform: uppercase;
      color: var(--ember); margin-bottom: 0.25rem;
    }
    .best-name {
      font-family: 'Playfair Display', serif; font-size: 1.8rem;
      font-weight: 700; line-height: 1.1; margin-bottom: 0.5rem;
    }
    .best-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }
    .tag-pill {
      padding: 0.2rem 0.6rem; border-radius: 999px;
      font-size: 0.75rem; font-family: 'DM Mono', monospace;
    }
    .tag-pill.matched   { background: var(--rust); color: #fff; }
    .tag-pill.unmatched { background: rgba(255,255,255,0.1); color: rgba(245,239,230,0.5); }
    .best-score {
      font-family: 'Playfair Display', serif; font-size: 2.2rem;
      font-weight: 700; color: var(--ember);
      text-align: right; flex-shrink: 0;
    }
    .best-score span {
      display: block; font-family: 'DM Mono', monospace;
      font-size: 0.6rem; letter-spacing: 0.15em; text-transform: uppercase;
      color: var(--muted); text-align: center; margin-top: 0.1rem;
    }
    .food-list { display: flex; flex-direction: column; gap: 0.6rem; }
    .food-row {
      display: flex; align-items: center; gap: 1rem;
      padding: 0.85rem 1.1rem; background: #fff;
      border: 1.5px solid var(--warm); border-radius: 8px;
      animation: slideUp 0.35s ease both;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .food-row:hover {
      border-color: var(--rust);
      box-shadow: 0 2px 12px rgba(192,82,42,0.08);
    }
    .food-row-emoji { font-size: 1.6rem; flex-shrink: 0; }
    .food-row-name {
      font-family: 'Playfair Display', serif; font-size: 1rem;
      font-weight: 700; color: var(--bark); flex: 1;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .food-row-bar-wrap {
      flex: 2; height: 6px; background: var(--warm);
      border-radius: 999px; overflow: hidden;
    }
    .food-row-bar {
      height: 100%; background: var(--rust); border-radius: 999px;
      transition: width 0.6s cubic-bezier(0.4,0,0.2,1);
    }
    .food-row-pct {
      font-family: 'DM Mono', monospace; font-size: 0.78rem;
      color: var(--muted); width: 2.5rem; text-align: right; flex-shrink: 0;
    }
    .no-match { text-align: center; padding: 2.5rem; color: var(--muted); font-style: italic; }
    .error-msg {
      color: var(--rust); font-size: 0.85rem; margin-top: 0.5rem;
      font-family: 'DM Mono', monospace;
    }
    .section-label {
      font-family: 'DM Mono', monospace; font-size: 0.65rem;
      letter-spacing: 0.2em; text-transform: uppercase;
      color: var(--muted); margin: 1.25rem 0 0.75rem;
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(14px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .food-row:nth-child(1) { animation-delay: 0.05s; }
    .food-row:nth-child(2) { animation-delay: 0.10s; }
    .food-row:nth-child(3) { animation-delay: 0.15s; }
    .food-row:nth-child(4) { animation-delay: 0.20s; }
    .food-row:nth-child(5) { animation-delay: 0.25s; }
    .food-row:nth-child(6) { animation-delay: 0.30s; }
    .food-row:nth-child(7) { animation-delay: 0.35s; }
    .food-row:nth-child(8) { animation-delay: 0.40s; }
    @media (max-width: 540px) {
      .best-card { flex-wrap: wrap; }
      .best-score { width: 100%; text-align: left; }
      .food-row-bar-wrap { flex: 1; }
    }
  </style>
</head>
<body>
  <header>
    <p class="header-tag">Food Recommender</p>
    <h1>What are you <span>craving?</span></h1>
    <p class="header-sub">Describe a feeling, taste, or texture — we'll find the match.</p>
  </header>

  <main>
    <div class="input-section">
      <label class="input-label" for="craving-input">Your craving</label>
      <div class="input-row">
        <input id="craving-input" type="text"
               placeholder="something warm and cheesy…"
               autocomplete="off" spellcheck="false"/>
        <button id="match-btn">Match →</button>
      </div>
      <div id="error-msg" class="error-msg" style="display:none;"></div>
      <div class="chips">
        <div class="chip" data-val="crispy and salty">crispy &amp; salty</div>
        <div class="chip" data-val="warm and comforting">warm &amp; comforting</div>
        <div class="chip" data-val="sweet and fruity">sweet &amp; fruity</div>
        <div class="chip" data-val="light and fresh">light &amp; fresh</div>
        <div class="chip" data-val="rich and cheesy">rich &amp; cheesy</div>
        <div class="chip" data-val="greasy and savory">greasy &amp; savory</div>
      </div>
    </div>

    <div id="results">
      <p class="results-heading">Results for <strong id="craving-display"></strong></p>
      <div id="best-card-wrap"></div>
      <p class="section-label">All matches</p>
      <div id="food-list" class="food-list"></div>
    </div>
  </main>

  <script>
    const input   = document.getElementById('craving-input');
    const btn     = document.getElementById('match-btn');
    const results = document.getElementById('results');
    const errMsg  = document.getElementById('error-msg');

    document.querySelectorAll('.chip').forEach(c =>
      c.addEventListener('click', () => { input.value = c.dataset.val; doMatch(); })
    );
    btn.addEventListener('click', doMatch);
    input.addEventListener('keydown', e => { if (e.key === 'Enter') doMatch(); });

    async function doMatch() {
      const craving = input.value.trim();
      errMsg.style.display = 'none';
      if (!craving) {
        errMsg.textContent = "Please describe what you're craving.";
        errMsg.style.display = 'block';
        return;
      }
      btn.textContent = '…'; btn.disabled = true;
      try {
        const res  = await fetch('/match', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ craving })
        });
        const data = await res.json();
        if (data.error) { errMsg.textContent = data.error; errMsg.style.display = 'block'; return; }
        renderResults(data);
      } catch(e) {
        errMsg.textContent = 'Something went wrong. Please try again.';
        errMsg.style.display = 'block';
      } finally {
        btn.textContent = 'Match →'; btn.disabled = false;
      }
    }

    function renderResults(data) {
      document.getElementById('craving-display').textContent = '"' + data.craving + '"';
      results.style.display = 'block';

      const best  = data.results[0];
      const bWrap = document.getElementById('best-card-wrap');
      if (!best || best.score === 0) {
        bWrap.innerHTML = '<div class="no-match">No close matches found — try different words!</div>';
      } else {
        const matchedSet = new Set(best.matched_tags);
        const tagPills   = best.all_tags.map(t =>
          '<span class="tag-pill ' + (matchedSet.has(t) ? 'matched' : 'unmatched') + '">' + t + '</span>'
        ).join('');
        bWrap.innerHTML =
          '<div class="best-card">' +
            '<div class="best-emoji">' + best.emoji + '</div>' +
            '<div class="best-info">' +
              '<p class="best-label">Best match</p>' +
              '<p class="best-name">'  + best.name  + '</p>' +
              '<div class="best-tags">' + tagPills + '</div>' +
            '</div>' +
            '<div class="best-score">' + best.score + '%<span>match</span></div>' +
          '</div>';
      }

      document.getElementById('food-list').innerHTML = data.results.map(f =>
        '<div class="food-row">' +
          '<span class="food-row-emoji">' + f.emoji + '</span>' +
          '<span class="food-row-name">'  + f.name  + '</span>' +
          '<div class="food-row-bar-wrap"><div class="food-row-bar" style="width:' + f.score + '%"></div></div>' +
          '<span class="food-row-pct">'   + f.score + '%</span>' +
        '</div>'
      ).join('');

      results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  </script>
</body>
</html>"""

if __name__ == "__main__":
    app.run(debug=True)
