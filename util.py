from collections import deque


def shortest_path(start, goal, get_neighbors):
    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for next_cell in get_neighbors(*current):
            if next_cell not in came_from:
                came_from[next_cell] = current
                queue.append(next_cell)

    if goal not in came_from:
        return [start]

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path