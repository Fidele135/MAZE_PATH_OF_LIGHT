from pathlib import Path


def load_level(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        return [line.rstrip("\n") for line in file]


def load_all_levels():
    levels_folder = Path(__file__).with_name("levels")
    level_files = sorted(levels_folder.glob("level*.txt"))
    return [load_level(file) for file in level_files]