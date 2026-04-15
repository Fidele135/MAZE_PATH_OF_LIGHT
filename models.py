class Entity:
    def __init__(self, row: int, col: int, color: str):
        self.row = row
        self.col = col
        self.start_row = row
        self.start_col = col
        self.color = color

    def reset(self):
        self.row = self.start_row
        self.col = self.start_col


class LightBeam(Entity):
    def __init__(self, row: int, col: int, color: str, lives: int):
        super().__init__(row, col, color)
        self.score = 0
        self.lives = lives
        self.energy_ticks = 0

    @property
    def energized(self) -> bool:
        return self.energy_ticks > 0


class Shadow(Entity):
    def __init__(self, row: int, col: int, color: str):
        super().__init__(row, col, color)
        self.afraid = False