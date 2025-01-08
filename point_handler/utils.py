"""Utility functions for the point_handler module."""


def distance_between_points(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Calculate the Euclidean distance between two points.

    Args:
        p1 (tuple): The first point as a tuple of (x, y) coordinates.
        p2 (tuple): The second point as a tuple of (x, y) coordinates.

    Returns:
        float: The Euclidean distance between the two points.
    """
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
