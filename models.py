class Entity:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.start_row = row
        self.start_col = col
        self.color = color

    def reset(self):
        self.row = self.start_row
        self.col = self.start_col


class LightBeam(Entity):
    def __init__(self, row, col, color, lives):
        super().__init__(row, col, color)
        self.lives = lives
        self.score = 0
        self.direction = None
        self.previous_position = None
        self.waiting_for_input = True

    def stop(self):
        self.direction = None
        self.previous_position = None
        self.waiting_for_input = True

    def start_moving(self, direction):
        self.direction = direction
        self.waiting_for_input = False