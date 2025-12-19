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


def draw_points_on_court(
    config: CourtConfiguration,
    xy: Optional[np.ndarray] = None,
    labels: Optional[list[str]] = None,
    fill_color: Optional[sv.Color] = sv.Color.BLACK,
    text_color: sv.Color = sv.Color.WHITE,
    edge_color: Optional[sv.Color] = sv.Color.WHITE,
    size: int = 30,
    edge_thickness: Optional[int] = None,
    scale: float = 20,
    padding: int = 50,
    line_thickness: int = 6,
    court: Optional[np.ndarray] = None,
) -> np.ndarray:
    if court is None:
        court = draw_court(
            config=config,
            scale=scale,
            padding=padding,
            line_thickness=line_thickness,
        )

    if xy is None or np.size(xy) == 0:
        return court

    pts = np.atleast_2d(xy)
    n = pts.shape[0]

    labels = labels if labels is not None else [None] * n
    if len(labels) < n:
        labels = list(labels) + [None] * (n - len(labels))

    stroke = edge_thickness if edge_thickness is not None else max(2, line_thickness // 2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.4, size / 28.0)
    font_thickness = max(1, size // 8)

    for i in range(n):
        cx, cy = _to_pixel((float(pts[i, 0]), float(pts[i, 1])), scale=scale, padding=padding)

        if fill_color is not None:
            cv2.circle(court, (cx, cy), size, fill_color.as_bgr(), -1, lineType=cv2.LINE_AA)

        if edge_color is not None and stroke > 0:
            cv2.circle(court, (cx, cy), size, edge_color.as_bgr(), stroke, lineType=cv2.LINE_AA)

        label = labels[i]
        if label is not None and str(label) != "":
            text = str(label)
            (tw, th), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
            tx = int(cx - tw / 2)
            ty = int(cy + th / 2)
            cv2.putText(
                court,
                text,
                (tx, ty),
                font,
                font_scale,
                text_color.as_bgr(),
                font_thickness,
                lineType=cv2.LINE_AA,
            )

    return court


def draw_paths_on_court(
    config: CourtConfiguration,
    paths: List[np.ndarray],
    color: Optional[sv.Color] = sv.Color.BLACK,
    thickness: Optional[int] = None,
    scale: float = 20,
    padding: int = 50,
    line_thickness: int = 6,
    court: Optional[np.ndarray] = None,
) -> np.ndarray:
    if court is None:
        court = draw_court(
            config=config,
            scale=scale,
            padding=padding,
            line_thickness=line_thickness,
        )

    if not paths or color is None:
        return court

    stroke = thickness if thickness is not None else line_thickness
    bgr = color.as_bgr()

    def to_segments(pts: np.ndarray) -> list[np.ndarray]:
        pts = np.atleast_2d(pts).astype(float)
        segments: list[np.ndarray] = []
        cur: list[np.ndarray] = []
        for p in pts:
            if np.isnan(p).any():
                if cur:
                    segments.append(np.asarray(cur, dtype=float))
                    cur = []
            else:
                cur.append(p)
        if cur:
            segments.append(np.asarray(cur, dtype=float))
        return segments

    for path in paths:
        if path is None or np.size(path) == 0:
            continue

        for seg in to_segments(path):
            if seg.shape[0] >= 2:
                poly = np.array(
                    [[_to_pixel((float(x), float(y)), scale, padding) for x, y in seg]],
                    dtype=np.int32,
                )
                cv2.polylines(
                    img=court,
                    pts=poly,
                    isClosed=False,
                    color=bgr,
                    thickness=stroke,
                    lineType=cv2.LINE_AA,
                )
            elif seg.shape[0] == 1:
                cx, cy = _to_pixel((float(seg[0, 0]), float(seg[0, 1])), scale, padding)
                cv2.circle(
                    img=court,
                    center=(cx, cy),
                    radius=max(1, stroke // 2),
                    color=bgr,
                    thickness=-1,
                    lineType=cv2.LINE_AA,
                )

    return court

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