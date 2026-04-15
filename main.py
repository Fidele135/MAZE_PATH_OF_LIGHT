import tkinter as tk
from game import MazePathGame


def main():
    root = tk.Tk()
    MazePathGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()