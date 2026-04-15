from pathlib import Path


def load_level(path):
    with open(path, "r", encoding="utf-8") as file:
        return [line.rstrip("\n") for line in file]


def load_all_levels():
    folder = Path(__file__).with_name("levels")
    files = sorted(folder.glob("level*.txt"))
    return [load_level(file) for file in files]