import tkinter as tk
from pathlib import Path

from config import (
    CELL_SIZE,
    HUD_HEIGHT,
    GAME_TICK_MS,
    STARTING_LIVES,
    CRYSTAL_POINTS,
    LEVEL_COMPLETE_BONUS,
    TEXT_COLOR,
    LEVEL_THEMES,
)
from models import LightBeam
from level import MazeLevel
from loader import load_all_levels
from util import direction_from_key
from scoreboard import ScoreBoard


SCORES_FILE = Path(__file__).with_name("maze_scores.json")


class PathOfLightGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Path of Light")

        self.scoreboard = ScoreBoard(SCORES_FILE)
        self.level_maps = load_all_levels()
        self.level_index = 0
        self.level = MazeLevel(self.level_maps[self.level_index])
        self.theme = self.get_theme()

        start_row, start_col = self.level.player_start
        self.player = LightBeam(
            start_row,
            start_col,
            self.theme["player"],
            STARTING_LIVES,
        )

        self.game_over = False
        self.win = False
        self.message = "Choose a direction to start."

        width = self.level.width * CELL_SIZE
        height = self.level.height * CELL_SIZE + HUD_HEIGHT

        self.canvas = tk.Canvas(
            root,
            width=width,
            height=height,
            bg=self.theme["background"],
            highlightthickness=0,
        )
        self.canvas.pack()

        self.restart_button = tk.Button(
            root,
            text="Restart Game",
            command=self.restart_game,
        )
        self.restart_button.pack(pady=6)

        self.root.bind("<KeyPress>", self.handle_key)
        self.loop()

    def get_theme(self):
        return LEVEL_THEMES[self.level_index % len(LEVEL_THEMES)]

    def handle_key(self, event):
        if self.game_over:
            return

        direction = direction_from_key(event.keysym)
        if direction and self.player.waiting_for_input:
            if self.can_move(direction):
                self.player.start_moving(direction)
                self.message = "The light is moving."
            else:
                self.message = "That path is blocked."

    def can_move(self, direction):
        dr, dc = direction
        nr = self.player.row + dr
        nc = self.player.col + dc
        return self.level.is_walkable(nr, nc)

    def loop(self):
        if not self.game_over and self.player.direction:
            self.move_step()

        self.draw()
        self.root.after(GAME_TICK_MS, self.loop)

    def move_step(self):
        dr, dc = self.player.direction
        nr = self.player.row + dr
        nc = self.player.col + dc

        if not self.level.is_walkable(nr, nc):
            self.player.stop()
            self.message = "Choose a new direction."
            return

        self.player.previous_position = (self.player.row, self.player.col)
        self.player.row = nr
        self.player.col = nc

        if self.level.is_trap(nr, nc):
            self.player.lives -= 1
            if self.player.lives <= 0:
                self.game_over = True
                self.win = False
                self.message = "Game Over."
                self.scoreboard.save_result(self.player.score)
            else:
                self.message = "Trap hit. Restarting level."
                self.restart_level()
            return

        points = self.level.collect_crystal_at(nr, nc)
        if points:
            self.player.score += CRYSTAL_POINTS
            self.message = "Crystal collected."

        if self.level.is_exit(nr, nc):
            self.player.score += LEVEL_COMPLETE_BONUS
            self.next_level()
            return

        self.check_crossroad()

    def check_crossroad(self):
        neighbors = self.level.valid_neighbors(self.player.row, self.player.col)
        if len(neighbors) > 2:
            self.player.stop()
            self.message = "Crossroad reached. Choose a path."

    def restart_level(self):
        self.level.reset()
        start_row, start_col = self.level.player_start
        self.player.row = start_row
        self.player.col = start_col
        self.player.color = self.theme["player"]
        self.player.stop()

    def restart_game(self):
        self.level_index = 0
        self.level = MazeLevel(self.level_maps[self.level_index])
        self.theme = self.get_theme()

        start_row, start_col = self.level.player_start
        self.player.row = start_row
        self.player.col = start_col
        self.player.lives = STARTING_LIVES
        self.player.score = 0
        self.player.color = self.theme["player"]
        self.player.stop()

        self.canvas.configure(bg=self.theme["background"])
        self.game_over = False
        self.win = False
        self.message = "Game restarted."

    def next_level(self):
        self.level_index += 1

        if self.level_index >= len(self.level_maps):
            self.game_over = True
            self.win = True
            self.message = "You finished all levels."
            self.scoreboard.save_result(self.player.score)
            return

        self.level = MazeLevel(self.level_maps[self.level_index])
        self.theme = self.get_theme()

        start_row, start_col = self.level.player_start
        self.player.row = start_row
        self.player.col = start_col
        self.player.color = self.theme["player"]
        self.player.stop()

        self.canvas.configure(bg=self.theme["background"])
        self.message = f"Level {self.level_index + 1} started."

    def draw(self):
        self.canvas.delete("all")
        self.draw_hud()
        self.draw_board()
        self.draw_player()

        if self.game_over:
            self.draw_overlay()

    def draw_hud(self):
        width = self.level.width * CELL_SIZE

        self.canvas.create_rectangle(
            0, 0, width, HUD_HEIGHT,
            fill="#111111",
            outline="#333333",
        )

        hud_text = (
            f"Level: {self.level_index + 1}    "
            f"Score: {self.player.score}    "
            f"Best: {self.scoreboard.best_score}    "
            f"Lives: {self.player.lives}    "
            f"Crystals Left: {self.level.remaining_crystals}"
        )

        self.canvas.create_text(
            12, 20,
            anchor="w",
            text=hud_text,
            fill=TEXT_COLOR,
            font=("Consolas", 13, "bold"),
        )

        self.canvas.create_text(
            12, 48,
            anchor="w",
            text=self.message,
            fill="#dddddd",
            font=("Consolas", 10),
        )

    def draw_board(self):
        for row in range(self.level.height):
            for col in range(self.level.width):
                x1 = col * CELL_SIZE
                y1 = HUD_HEIGHT + row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell = self.level.get_cell(row, col)
                fill_color = self.theme["path"]

                if cell == "#":
                    fill_color = self.theme["wall"]
                elif cell == "X":
                    fill_color = self.theme["exit"]
                elif cell == "T":
                    fill_color = self.theme["trap"]

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill_color,
                    outline="#222222",
                )

                if cell == "C":
                    self.canvas.create_oval(
                        x1 + 8, y1 + 8, x2 - 8, y2 - 8,
                        fill=self.theme["crystal"],
                        outline=self.theme["crystal"],
                    )

    def draw_player(self):
        x1 = self.player.col * CELL_SIZE + 6
        y1 = HUD_HEIGHT + self.player.row * CELL_SIZE + 6
        x2 = (self.player.col + 1) * CELL_SIZE - 6
        y2 = HUD_HEIGHT + (self.player.row + 1) * CELL_SIZE - 6

        self.canvas.create_oval(
            x1, y1, x2, y2,
            fill=self.player.color,
            outline="",
        )

    def draw_overlay(self):
        width = self.level.width * CELL_SIZE
        height = self.level.height * CELL_SIZE + HUD_HEIGHT

        self.canvas.create_rectangle(
            0, 0, width, height,
            fill="black",
            stipple="gray50",
        )

        title = "YOU WIN" if self.win else "GAME OVER"

        self.canvas.create_text(
            width / 2,
            height / 2 - 20,
            text=title,
            fill="white",
            font=("Consolas", 26, "bold"),
        )

        self.canvas.create_text(
            width / 2,
            height / 2 + 16,
            text=f"Final Score: {self.player.score}",
            fill="white",
            font=("Consolas", 12),
        )