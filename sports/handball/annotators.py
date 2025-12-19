import cv2
import numpy as np
import supervision as sv
from typing import Tuple, Optional, List

from sports.handball.config import CourtConfiguration


def _to_pixel(point: Tuple[float, float], scale: float, padding: int) -> Tuple[int, int]:
    return (
        int(round(point[0] * scale + padding)),
        int(round(point[1] * scale + padding)),
    )


def _draw_dashed_line(
    image: np.ndarray,
    p0: Tuple[int, int],
    p1: Tuple[int, int],
    color: Tuple[int, int, int],
    thickness: int,
    dash_px: int = 20,
    gap_px: int = 14,
) -> None:
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    dist = float(np.hypot(dx, dy))
    if dist < 1e-6:
        return

    ux, uy = dx / dist, dy / dist
    t = 0.0
    while t < dist:
        t2 = min(t + dash_px, dist)
        a = (int(round(x0 + ux * t)), int(round(y0 + uy * t)))
        b = (int(round(x0 + ux * t2)), int(round(y0 + uy * t2)))
        cv2.line(image, a, b, color, thickness, lineType=cv2.LINE_AA)
        t = t2 + gap_px


def draw_court(
    config: CourtConfiguration,
    scale: float = 20,
    padding: int = 50,
    line_thickness: int = 4,
    line_color: sv.Color = sv.Color.WHITE,
    background_color: sv.Color = sv.Color(224, 190, 139),
) -> np.ndarray:
    """Render a handball court to an image."""
    court_h_px = int(round(config.court_width * scale))
    court_l_px = int(round(config.court_length * scale))

    image = np.zeros((court_h_px + 2 * padding, court_l_px + 2 * padding, 3), dtype=np.uint8)
    image[:, :] = background_color.as_bgr()

    # solid lines from config.edges
    for a, b in config.edges:
        p0 = _to_pixel(config.vertices[a], scale, padding)
        p1 = _to_pixel(config.vertices[b], scale, padding)
        cv2.line(image, p0, p1, line_color.as_bgr(), line_thickness, lineType=cv2.LINE_AA)

    # dashed 9m lines (indices from your config)
    for a, b in [(16, 17), (18, 19)]:
        p0 = _to_pixel(config.vertices[a], scale, padding)
        p1 = _to_pixel(config.vertices[b], scale, padding)
        _draw_dashed_line(
            image=image,
            p0=p0,
            p1=p1,
            color=line_color.as_bgr(),
            thickness=line_thickness,
            dash_px=max(14, line_thickness * 5),
            gap_px=max(10, line_thickness * 4),
        )

    # center spot (index 36)
    c = _to_pixel(config.vertices[config.center_spot_index], scale, padding)
    cv2.circle(image, c, max(2, line_thickness), line_color.as_bgr(), -1, lineType=cv2.LINE_AA)

    return image