import json
from pathlib import Path


class ScoreBoard:
    def __init__(self, path):
        self.path = path
        self.best_score = 0
        self.games_played = 0
        self.load()

    def load(self):
        if self.path.exists():
            data = json.loads(self.path.read_text())
            self.best_score = data.get("best_score", 0)
            self.games_played = data.get("games_played", 0)

    def save_result(self, score):
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