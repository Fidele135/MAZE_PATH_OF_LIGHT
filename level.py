class MazeLevel:
    WALL = "#"
    ORB = "."
    ENERGY = "o"
    EMPTY = " "
    PLAYER = "P"
    SHADOW = "S"
    EXIT = "X"

    def __init__(self, level_map):
        self.original = [list(row) for row in level_map]
        self.height = len(self.original)
        self.width = len(self.original[0])
        self.grid = []
        self.player_start = (1, 1)
        self.shadow_starts = []
        self.exit_pos = None
        self.remaining_orbs = 0
        self.reset()

    def reset(self):
        self.grid = [row[:] for row in self.original]
        self.shadow_starts = []
        self.exit_pos = None
        self.remaining_orbs = 0

        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if cell == self.PLAYER:
                    self.player_start = (row_index, col_index)
                    self.grid[row_index][col_index] = self.EMPTY
                elif cell == self.SHADOW:
                    self.shadow_starts.append((row_index, col_index))
                    self.grid[row_index][col_index] = self.EMPTY
                elif cell == self.EXIT:
                    self.exit_pos = (row_index, col_index)
                elif cell in (self.ORB, self.ENERGY):
                    self.remaining_orbs += 1

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.height and 0 <= col < self.width

    def is_wall(self, row: int, col: int) -> bool:
        return self.grid[row][col] == self.WALL

    def is_walkable(self, row: int, col: int) -> bool:
        return self.in_bounds(row, col) and not self.is_wall(row, col)

    def is_energy_item(self, row: int, col: int) -> bool:
        return self.grid[row][col] == self.ENERGY

    def collect_at(self, row: int, col: int):
        cell = self.grid[row][col]

        if cell == self.ORB:
            self.grid[row][col] = self.EMPTY
            self.remaining_orbs -= 1
            return 10

        if cell == self.ENERGY:
            self.grid[row][col] = self.EMPTY
            self.remaining_orbs -= 1
            return 50

        return 0