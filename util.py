def direction_from_key(keysym):
    directions = {
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
    return directions.get(keysym)