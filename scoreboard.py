import json
from pathlib import Path


class ScoreBoard:
    def __init__(self, path: Path):
        self.path = path
        self.best_score = 0
        self.games_played = 0
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self.best_score = int(data.get("best_score", 0))
                self.games_played = int(data.get("games_played", 0))
            except Exception:
                self.best_score = 0
                self.games_played = 0

    def save_result(self, score: int):
        self.games_played += 1
        self.best_score = max(self.best_score, score)
        self.path.write_text(
            json.dumps(
                {
                    "best_score": self.best_score,
                    "games_played": self.games_played,
                },
                indent=2,
            )
        )