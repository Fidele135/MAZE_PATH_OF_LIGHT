import tkinter as tk
from pathlib import Path
import random

from config import (
    CELL_SIZE,
    HUD_HEIGHT,
    PLAYER_STEP_MS,
    SHADOW_STEP_MS,
    STARTING_LIVES,
    ORB_POINTS,
    ENERGY_POINTS,
    SHADOW_BONUS,
    LEVEL_COMPLETE_BONUS,
    ENERGY_TICKS,
    PLAYER_COLOR,
    SHADOW_COLOR,
    WALL_COLOR,
    FLOOR_COLOR,
    ORB_COLOR,
    ENERGY_COLOR,
    EXIT_COLOR,
    TEXT_COLOR,
)
from scoreboard import ScoreBoard
from models import LightBeam, Shadow
from level import MazeLevel
from loader import load_all_levels
from util import shortest_path


SCORES_FILE = Path(__file__).with_name("maze_scores.json")


class MazePathGame:
    DIRECTIONS = {
        "Up": (-1, 0),
        "Down": (1, 0),
        "Left": (0, -1),
        "Right": (0, 1),
        "w": (-1, 0),
        "s": (1, 0),
        "a": (0, -1),
        "d": (0, 1),
        "W": (-1, 0),
        "S": (1, 0),
        "A": (0, -1),
        "D": (0, 1),
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Maze Path of Light")

        self.scoreboard = ScoreBoard(SCORES_FILE)
        self.level_maps = load_all_levels()
        self.level_index = 0
        self.level = MazeLevel(self.level_maps[self.level_index])

        self.player = LightBeam(
            self.level.player_start[0],
            self.level.player_start[1],
            PLAYER_COLOR,
            STARTING_LIVES,
        )

        self.shadows = [
            Shadow(row, col, SHADOW_COLOR)
            for row, col in self.level.shadow_starts
        ]

        self.game_over = False
        self.win = False
        self.message = "Collect all light orbs, then reach the green exit."
        self.pending_move = None
        self.player_loop_id = None
        self.shadow_loop_id = None

        width = self.level.width * CELL_SIZE
        height = self.level.height * CELL_SIZE + HUD_HEIGHT

        self.canvas = tk.Canvas(
            root,
            width=width,
            height=height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.root.bind("<KeyPress>", self.handle_keypress)

        self.restart_button = tk.Button(
            root,
            text="Restart Game",
            command=self.restart_game,
        )
        self.restart_button.pack(pady=6)

        self.start_loops()
        self.draw()

    def start_loops(self):
        self.stop_loops()
        self.player_loop_id = self.root.after(PLAYER_STEP_MS, self.game_tick)
        self.shadow_loop_id = self.root.after(SHADOW_STEP_MS, self.shadow_tick)

    def stop_loops(self):
        if self.player_loop_id is not None:
            self.root.after_cancel(self.player_loop_id)
            self.player_loop_id = None

        if self.shadow_loop_id is not None:
            self.root.after_cancel(self.shadow_loop_id)
            self.shadow_loop_id = None

    def handle_keypress(self, event):
        if event.keysym in self.DIRECTIONS:
            self.pending_move = self.DIRECTIONS[event.keysym]

    def restart_game(self):
        self.level_index = 0
        self.level = MazeLevel(self.level_maps[self.level_index])
        self.player = LightBeam(
            self.level.player_start[0],
            self.level.player_start[1],
            PLAYER_COLOR,
            STARTING_LIVES,
        )
        self.shadows = [
            Shadow(row, col, SHADOW_COLOR)
            for row, col in self.level.shadow_starts
        ]
        self.game_over = False
        self.win = False
        self.message = "New journey of light has started."
        self.pending_move = None
        self.start_loops()
        self.draw()

    def next_level(self):
        self.level_index += 1

        if self.level_index >= len(self.level_maps):
            self.win = True
            self.game_over = True
            self.message = "You finished all levels of Maze Path of Light."
            self.finish_game()
            return

        old_score = self.player.score
        old_lives = self.player.lives

        self.level = MazeLevel(self.level_maps[self.level_index])
        self.player = LightBeam(
            self.level.player_start[0],
            self.level.player_start[1],
            PLAYER_COLOR,
            old_lives,
        )
        self.player.score = old_score

        self.shadows = [
            Shadow(row, col, SHADOW_COLOR)
            for row, col in self.level.shadow_starts
        ]

        self.message = f"Welcome to level {self.level_index + 1}"

    def finish_game(self):
        self.stop_loops()
        self.scoreboard.save_result(self.player.score)

    def game_tick(self):
        if not self.game_over and self.pending_move:
            self.move_player(*self.pending_move)

        if self.player.energy_ticks > 0:
            self.player.energy_ticks -= 1

        for shadow in self.shadows:
            shadow.afraid = self.player.energized

        self.draw()

        if not self.game_over:
            self.player_loop_id = self.root.after(PLAYER_STEP_MS, self.game_tick)

    def shadow_tick(self):
        if not self.game_over:
            for shadow in self.shadows:
                self.move_shadow(shadow)

            self.check_collisions()
            self.draw()
            self.shadow_loop_id = self.root.after(SHADOW_STEP_MS, self.shadow_tick)

    def move_player(self, delta_row: int, delta_col: int):
        next_row = self.player.row + delta_row
        next_col = self.player.col + delta_col

        if not self.level.is_walkable(next_row, next_col):
            self.message = "Wall blocked the light."
            return

        was_energy = self.level.is_energy_item(next_row, next_col)

        self.player.row = next_row
        self.player.col = next_col

        gained_points = self.level.collect_at(next_row, next_col)
        self.player.score += gained_points

        if was_energy:
            self.player.energy_ticks = ENERGY_TICKS
            self.message = "Energy core collected. Shadows fear the light."
        elif gained_points == ORB_POINTS:
            self.message = "Light orb collected."
        elif gained_points == ENERGY_POINTS:
            self.message = "Energy core collected."
        else:
            self.message = ""

        self.check_collisions()
        self.check_exit()

    def move_shadow(self, shadow: Shadow):
        neighbors = self.valid_neighbors(shadow.row, shadow.col)

        if not neighbors:
            return

        if shadow.afraid:
            best_cell = self.farthest_neighbor_from_player(neighbors)
            shadow.row, shadow.col = best_cell
            return

        path = shortest_path(
            (shadow.row, shadow.col),
            (self.player.row, self.player.col),
            self.valid_neighbors,
        )

        if len(path) >= 2:
            shadow.row, shadow.col = path[1]
        else:
            shadow.row, shadow.col = random.choice(neighbors)

    def valid_neighbors(self, row: int, col: int):
        neighbors = []

        for delta_row, delta_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_row = row + delta_row
            next_col = col + delta_col
            if self.level.is_walkable(next_row, next_col):
                neighbors.append((next_row, next_col))

        return neighbors

    def farthest_neighbor_from_player(self, neighbors):
        best = None
        best_distance = -1

        for cell in neighbors:
            distance = abs(cell[0] - self.player.row) + abs(cell[1] - self.player.col)
            if distance > best_distance:
                best_distance = distance
                best = cell

        return best

    def check_collisions(self):
        for shadow in self.shadows:
            if shadow.row == self.player.row and shadow.col == self.player.col:
                if self.player.energized:
                    self.player.score += SHADOW_BONUS
                    shadow.reset()
                    self.message = "Shadow defeated by the light."
                else:
                    self.player.lives -= 1
                    self.message = f"A shadow touched you. Lives left: {self.player.lives}"
                    self.reset_positions()

                    if self.player.lives <= 0:
                        self.game_over = True
                        self.message = "Game over. Darkness has won."
                        self.finish_game()
                break

    def reset_positions(self):
        self.player.reset()
        self.player.energy_ticks = 0

        for shadow in self.shadows:
            shadow.reset()
            shadow.afraid = False

    def check_exit(self):
        if (self.player.row, self.player.col) == self.level.exit_pos:
            if self.level.remaining_orbs == 0:
                self.player.score += LEVEL_COMPLETE_BONUS
                self.message = "Level complete. The path of light continues."
                self.next_level()
            else:
                self.message = "Collect all light orbs before using the exit."

    def draw(self):
        self.canvas.delete("all")
        self.draw_hud()
        self.draw_board()
        self.draw_entities()

        if self.game_over:
            self.draw_overlay()

    def draw_hud(self):
        width = self.level.width * CELL_SIZE
        self.canvas.create_rectangle(0, 0, width, HUD_HEIGHT, fill="#111", outline="#333")

        hud_text = (
            f"Level: {self.level_index + 1}    "
            f"Score: {self.player.score}    "
            f"Best: {self.scoreboard.best_score}    "
            f"Lives: {self.player.lives}    "
            f"Orbs Left: {self.level.remaining_orbs}"
        )

        self.canvas.create_text(
            12,
            18,
            anchor="w",
            text=hud_text,
            fill=TEXT_COLOR,
            font=("Consolas", 14, "bold"),
        )

        status_text = "ENERGIZED LIGHT MODE" if self.player.energized else self.message

        self.canvas.create_text(
            12,
            42,
            anchor="w",
            text=status_text,
            fill="lightgreen" if self.player.energized else "#ddd",
            font=("Consolas", 10),
        )

    def draw_board(self):
        for row in range(self.level.height):
            for col in range(self.level.width):
                x1 = col * CELL_SIZE
                y1 = HUD_HEIGHT + row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell = self.level.grid[row][col]

                if cell == MazeLevel.WALL:
                    fill_color = WALL_COLOR
                elif cell == MazeLevel.EXIT:
                    fill_color = EXIT_COLOR
                else:
                    fill_color = FLOOR_COLOR

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill_color,
                    outline="#222"
                )

                if cell == MazeLevel.ORB:
                    self.canvas.create_oval(
                        x1 + 10, y1 + 10, x2 - 10, y2 - 10,
                        fill=ORB_COLOR,
                        outline=ORB_COLOR
                    )

                elif cell == MazeLevel.ENERGY:
                    self.canvas.create_oval(
                        x1 + 6, y1 + 6, x2 - 6, y2 - 6,
                        fill=ENERGY_COLOR,
                        outline=ENERGY_COLOR
                    )

    def draw_entities(self):
        self.draw_entity(self.player.row, self.player.col, self.player.color, 5, 5)

        for shadow in self.shadows:
            color = "pink" if shadow.afraid else shadow.color
            self.draw_entity(shadow.row, shadow.col, color, 6, 6)

    def draw_entity(self, row, col, color, pad_x, pad_y):
        x1 = col * CELL_SIZE + pad_x
        y1 = HUD_HEIGHT + row * CELL_SIZE + pad_y
        x2 = (col + 1) * CELL_SIZE - pad_x
        y2 = HUD_HEIGHT + (row + 1) * CELL_SIZE - pad_y

        self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="")

    def draw_overlay(self):
        width = self.level.width * CELL_SIZE
        height = self.level.height * CELL_SIZE + HUD_HEIGHT

        self.canvas.create_rectangle(0, 0, width, height, fill="black", stipple="gray50")

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
            height / 2 + 18,
            text=f"Final Score: {self.player.score}   Best Score: {max(self.scoreboard.best_score, self.player.score)}",
            fill="white",
            font=("Consolas", 12),
        )

        self.canvas.create_text(
            width / 2,
            height / 2 + 48,
            text="Press Restart Game to play again.",
            fill="white",
            font=("Consolas", 12),
        )