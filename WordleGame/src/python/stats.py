import json
import shutil
from pathlib import Path
from datetime import date

DEFAULT_STATS = {
    "players": {}
}

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
STATS_PATH = DATA_DIR / "stats.json"
LEGACY_PATH = Path(__file__).resolve().parent / "stats.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

try:
    if not STATS_PATH.exists() and LEGACY_PATH.exists():
        shutil.move(str(LEGACY_PATH), str(STATS_PATH))
except Exception:
    pass

def load_stats():
    if not STATS_PATH.exists():
        save_stats(DEFAULT_STATS)
        return DEFAULT_STATS.copy()
    try:
        with STATS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_stats(DEFAULT_STATS)
        return DEFAULT_STATS.copy()

def save_stats(stats: dict):
    try:
        with STATS_PATH.open("w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Failed to save stats:", e)

# Compatibility wrappers for old frontend API
def load_stats_dict():
    return load_stats()

def save_stats_dict(d: dict):
    save_stats(d)

def update_player_stats(username=None, won=False, difficulty="EASY", attempts=0, player_name=None, **kwargs):
    name = (player_name or username or "ANON").strip() or "ANON"
    s = load_stats()
    players = s.setdefault("players", {})
    p = players.get(name, {
        "games": 0,
        "wins": 0,
        "score": 0,
        "last_difficulty": difficulty,
        "last_attempts": attempts,
        "avg_attempts": float(attempts),
        "last_play": str(date.today())
    })

    prev_games = p.get("games", 0)
    prev_avg = float(p.get("avg_attempts", attempts))
    p["games"] = prev_games + 1
    if won:
        p["wins"] = p.get("wins", 0) + 1
        p["score"] = p.get("score", 0) + 1
    p["last_difficulty"] = difficulty
    p["last_attempts"] = attempts
    p["avg_attempts"] = (prev_avg * prev_games + attempts) / p["games"]
    p["last_play"] = str(date.today())

    players[name] = p
    save_stats(s)
