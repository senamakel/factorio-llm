"""Plan movement into reach of a destination."""


def move_to(player, position, stop_distance=2.2):
    """Return a destination instruction; direction and timing belong to execution."""
    return {"kind":"move", "player":player["name"], "surface":player["surface"],
            "position":dict(position), "stop_distance":stop_distance}
