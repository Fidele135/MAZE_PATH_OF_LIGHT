import tkinter as tk
from game import PathOfLightGame


def main():
    root = tk.Tk()
    game = PathOfLightGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()