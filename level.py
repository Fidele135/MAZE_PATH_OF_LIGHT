class MazeLevel:
    WALL = "#"
    PATH = "."
    PLAYER = "P"
    EXIT = "X"
    CRYSTAL = "C"
    TRAP = "T"

    def __init__(self, level_map):
        self.original = [list(row) for row in level_map]
        self.height = len(self.original)
        self.width = len(self.original[0])
        self.reset()

    def reset(self):
        self.grid = [row[:] for row in self.original]
        self.player_start = (1, 1)
        self.exit_pos = None
        self.remaining_crystals = 0

        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == self.PLAYER:
                    self.player_start = (r, c)
                    self.grid[r][c] = self.PATH
                elif cell == self.EXIT:
                    self.exit_pos = (r, c)
                elif cell == self.CRYSTAL:
                    self.remaining_crystals += 1

    def is_walkable(self, r, c):
        if r < 0 or c < 0:
            return False
        if r >= self.height or c >= self.width:
            return False
        return self.grid[r][c] != self.WALL

    def get_cell(self, r, c):
        return self.grid[r][c]

    def collect_crystal_at(self, r, c):
        if self.grid[r][c] == self.CRYSTAL:
            self.grid[r][c] = self.PATH
            self.remaining_crystals -= 1
            return 100
        return 0

    def is_exit(self, r, c):
        return (r, c) == self.exit_pos

    def is_trap(self, r, c):
        return self.grid[r][c] == self.TRAP

    def valid_neighbors(self, r, c):
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr = r + dr
            nc = c + dc
            if self.is_walkable(nr, nc):
                neighbors.append((nr, nc))
        return neighbors