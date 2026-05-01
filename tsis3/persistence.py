import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

def load_json(filename, default):
    if not os.path.exists(filename): return default
    with open(filename, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_top_scores():
    return load_json(LEADERBOARD_FILE, [])

def save_score(name, score, distance):
    scores = get_top_scores()
    scores.append({"name": name, "score": score, "distance": int(distance)})
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    save_json(LEADERBOARD_FILE, scores)

def load_settings():
    default = {"sound": True, "car_color": "Blue", "difficulty": "Medium"}
    return load_json(SETTINGS_FILE, default)

def save_settings(settings):
    save_json(SETTINGS_FILE, settings)
