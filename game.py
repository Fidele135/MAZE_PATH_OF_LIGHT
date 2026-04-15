import tkinter as tk
from pathlib import Path

from config import *
from models import LightBeam
from level import MazeLevel
from loader import load_all_levels
from util import direction_from_key
from scoreboard import ScoreBoard


SCORES_FILE = Path("maze_scores.json")


class PathOfLightGame:

    def __init__(self, root):

        self.root = root
        self.root.title("Maze Path of Light")

        self.scoreboard = ScoreBoard(SCORES_FILE)

        self.level_maps = load_all_levels()
        self.level_index = 0
        self.level = MazeLevel(self.level_maps[0])

        r, c = self.level.player_start

        self.player = LightBeam(
            r,
            c,
            PLAYER_COLOR,
            STARTING_LIVES,
        )

        width = self.level.width * CELL_SIZE
        height = self.level.height * CELL_SIZE + HUD_HEIGHT

        self.canvas = tk.Canvas(
            root,
            width=width,
            height=height,
            bg="black",
        )

        self.canvas.pack()

        root.bind("<KeyPress>", self.handle_key)

        self.loop()

    def handle_key(self, event):

        direction = direction_from_key(event.keysym)

        if direction:

            if self.player.waiting_for_input:

                if self.can_move(direction):

                    self.player.start_moving(direction)

    def can_move(self, direction):

        dr, dc = direction

        nr = self.player.row + dr
        nc = self.player.col + dc

        return self.level.is_walkable(nr, nc)

    def loop(self):

        if self.player.direction:

            self.move_step()

        self.draw()

        self.root.after(
            GAME_TICK_MS,
            self.loop,
        )

    def move_step(self):

        dr, dc = self.player.direction

        nr = self.player.row + dr
        nc = self.player.col + dc

        if not self.level.is_walkable(nr, nc):

            self.player.stop()
            return

        self.player.previous_position = (
            self.player.row,
            self.player.col,
        )

        self.player.row = nr
        self.player.col = nc

        if self.level.is_exit(nr, nc):

            self.next_level()
            return

        if self.level.is_trap(nr, nc):

            self.player.lives -= 1
            self.restart_level()
            return

        points = self.level.collect_crystal_at(nr, nc)

        if points:

            self.player.score += points

        self.check_crossroad()

    def check_crossroad(self):

        neighbors = self.level.valid_neighbors(
            self.player.row,
            self.player.col,
        )

        if len(neighbors) > 2:

            self.player.stop()

    def restart_level(self):

        self.level.reset()

        r, c = self.level.player_start

        self.player.row = r
        self.player.col = c

        self.player.stop()

    def next_level(self):

        self.level_index += 1

        if self.level_index >= len(self.level_maps):

            print("YOU WIN")
            return

        self.level = MazeLevel(
            self.level_maps[self.level_index]
        )

        r, c = self.level.player_start

        self.player.row = r
        self.player.col = c

        self.player.stop()

    def draw(self):

        self.canvas.delete("all")

        for r in range(self.level.height):

            for c in range(self.level.width):

                x1 = c * CELL_SIZE
                y1 = HUD_HEIGHT + r * CELL_SIZE

                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell = self.level.get_cell(r, c)

                color = PATH_COLOR

                if cell == "#":
                    color = WALL_COLOR

                if cell == "X":
                    color = EXIT_COLOR

                if cell == "T":
                    color = TRAP_COLOR

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                )

                if cell == "C":

                    self.canvas.create_oval(
                        x1 + 8,
                        y1 + 8,
                        x2 - 8,
                        y2 - 8,
                        fill=CRYSTAL_COLOR,
                    )

        px1 = self.player.col * CELL_SIZE + 6
        py1 = HUD_HEIGHT + self.player.row * CELL_SIZE + 6

        px2 = (
            self.player.col + 1
        ) * CELL_SIZE - 6

        py2 = (
            HUD_HEIGHT
            + (self.player.row + 1)
            * CELL_SIZE
            - 6
        )

        self.canvas.create_oval(
            px1,
            py1,
            px2,
            py2,
            fill=PLAYER_COLOR,
        )