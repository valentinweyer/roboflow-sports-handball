import cv2
import numpy as np
import supervision as sv
from typing import Tuple, Optional, List
from sports.handball.config import CourtConfiguration
from sports.common.core import MeasurementUnit


def _to_pixel(
    point: Tuple[float, float],
    scale: float,
    padding: int,
    court_height: float = 2000.0,
) -> Tuple[int, int]:
    """Scale court point to pixel space and apply padding.

    y is flipped so court y=0 (bottom) maps to the bottom of the image
    and court y=court_height (top) maps to the top, matching real-world
    orientation and keeping the homography target space consistent.
    """
    return (
        int(round(point[0] * scale + padding)),
        int(round((court_height - point[1]) * scale + padding)),
    )


def _draw_dashed_line(
    image: np.ndarray,
    start: Tuple[int, int],
    end: Tuple[int, int],
    bgr_color: Tuple[int, int, int],
    thickness: int,
    dash_length: int = 20,
    gap_length: int = 10,
) -> None:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = np.sqrt(dx * dx + dy * dy)
    if distance < 1:
        return
    dx /= distance
    dy /= distance
    current_dist = 0
    while current_dist < distance:
        dash_start = (int(start[0] + dx * current_dist), int(start[1] + dy * current_dist))
        dash_end_dist = min(current_dist + dash_length, distance)
        dash_end = (int(start[0] + dx * dash_end_dist), int(start[1] + dy * dash_end_dist))
        cv2.line(image, dash_start, dash_end, bgr_color, thickness)
        current_dist += dash_length + gap_length


def _draw_goal_zone(
    image: np.ndarray,
    court_x0: float,
    g_y0: float,
    g_y1: float,
    radius_cm: float,
    side: str,
    scale: float,
    padding: int,
    court_rect_px: Tuple[int, int, int, int],  # x, y, w, h in pixels
    bgr_color: Tuple[int, int, int],
    thickness: int,
    dashed: bool = False,
) -> None:
    """
    Draw two quarter-circle arcs + straight line for one goal zone,
    clipped to the court boundary.

    Arcs are computed in court coordinates (y-up, matches matplotlib test script),
    converted to pixel coords, drawn onto a temporary layer, then masked to the
    court rectangle before blending onto the image.
    """
    n = 400
    direction = 1.0 if side == "left" else -1.0
    r = radius_cm

    t_upper = np.linspace(np.pi / 2, 0, n)
    t_lower = np.linspace(0, -np.pi / 2, n)

    # Only the two quarter-circle arcs — straight segment is drawn via config.edges
    arc_upper = np.array([[court_x0 + direction * r * np.cos(t), g_y1 + r * np.sin(t)] for t in t_upper])
    arc_lower = np.array([[court_x0 + direction * r * np.cos(t), g_y0 + r * np.sin(t)] for t in t_lower])

    # Draw onto a scratch layer the same size as image
    layer = np.zeros_like(image)

    def draw_arc_segment(seg):
        px_pts = np.array([[_to_pixel((float(p[0]), float(p[1])), scale, padding)] for p in seg], dtype=np.int32)
        if dashed:
            # Distance-based dashing so spacing is consistent regardless of n or scale
            dash_px = max(8, int(15 * scale))
            gap_px  = max(5, int(10 * scale))
            draw = True
            bucket = 0.0
            for i in range(len(px_pts) - 1):
                p1 = tuple(px_pts[i][0])
                p2 = tuple(px_pts[i+1][0])
                seg_len = float(np.hypot(p2[0] - p1[0], p2[1] - p1[1]))
                if draw:
                    cv2.line(layer, p1, p2, bgr_color, thickness)
                bucket += seg_len
                threshold = dash_px if draw else gap_px
                if bucket >= threshold:
                    bucket = 0.0
                    draw = not draw
        else:
            cv2.polylines(layer, [px_pts], False, bgr_color, thickness, cv2.LINE_AA)

    for seg in (arc_upper, arc_lower):
        draw_arc_segment(seg)

    # Mask to court boundary
    cx, cy, cw, ch = court_rect_px
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.rectangle(mask, (cx, cy), (cx + cw, cy + ch), 255, -1)
    layer[mask == 0] = 0

    # Blend onto image
    image[layer > 0] = layer[layer > 0]


def draw_court(
    config: CourtConfiguration,
    scale: float = 10,
    padding: int = 50,
    line_thickness: int = 4,
    line_color: sv.Color = sv.Color.WHITE,
    background_color: sv.Color = sv.Color(200, 160, 120),
    goal_area_color: Optional[sv.Color] = None,
) -> np.ndarray:
    court_height_px = int(round(config.court_width * scale))
    court_length_px = int(round(config.court_length * scale))
    center_circle_radius_px = int(round(config.center_circle_radius * scale))

    image = np.zeros(
        (court_height_px + 2 * padding, court_length_px + 2 * padding, 3),
        dtype=np.uint8,
    )
    image[:, :] = background_color.as_bgr()

    g_y0 = config.vertices[3][1]  # KP04 lower post
    g_y1 = config.vertices[2][1]  # KP03 upper post

    court_rect_px = (padding, padding, court_length_px, court_height_px)

    # Goal area fill
    if goal_area_color is not None:
        for side, post_x in [("left", 0.0), ("right", float(config.court_length))]:
            direction = 1.0 if side == "left" else -1.0
            r = config.goal_area_radius
            n = 300
            t_upper = np.linspace(np.pi / 2, 0, n)
            t_lower = np.linspace(0, -np.pi / 2, n)
            arc_upper = [[post_x + direction * r * np.cos(t), g_y1 + r * np.sin(t)] for t in t_upper]
            arc_lower = [[post_x + direction * r * np.cos(t), g_y0 + r * np.sin(t)] for t in t_lower]
            poly_pts = (
                [[post_x, g_y1]] + arc_upper +
                [[post_x + direction * r, g_y0]] + arc_lower +
                [[post_x, g_y0]]
            )
            poly_px = np.array(
                [[_to_pixel((float(p[0]), float(p[1])), scale, padding)] for p in poly_pts],
                dtype=np.int32,
            )
            cv2.fillPoly(image, [poly_px.reshape(-1, 2)], goal_area_color.as_bgr())

    # Court boundary edges — skip 6m/9m straight segments, drawn below from radius
    skip_edges = {(7, 8), (8, 7), (24, 25), (25, 24),
                  (33, 34), (34, 33), (35, 36), (36, 35)}
    for start_idx, end_idx in config.edges:
        if (start_idx, end_idx) in skip_edges:
            continue
        cv2.line(image,
                 _to_pixel(config.vertices[start_idx], scale, padding),
                 _to_pixel(config.vertices[end_idx],   scale, padding),
                 line_color.as_bgr(), line_thickness)

    # 6m and 9m straight segments drawn from radius so they align exactly with arcs
    g_y0_px = _to_pixel((0, g_y0), scale, padding)[1]
    g_y1_px = _to_pixel((0, g_y1), scale, padding)[1]
    for side, post_x in [("left", 0.0), ("right", float(config.court_length))]:
        direction = 1.0 if side == "left" else -1.0
        for r in [config.goal_area_radius, config.free_throw_line_distance]:
            tx = _to_pixel((post_x + direction * r, 0), scale, padding)[0]
            cv2.line(image, (tx, g_y0_px), (tx, g_y1_px), line_color.as_bgr(), line_thickness)

    # Center circle (no diameter lines)
    cv2.circle(image,
               _to_pixel(config.vertices[16], scale, padding),
               center_circle_radius_px,
               line_color.as_bgr(), line_thickness)

    # Goal area arcs (6m solid, 9m dashed) — clipped to court
    for side, post_x in [("left", 0.0), ("right", float(config.court_length))]:
        _draw_goal_zone(image, post_x, g_y0, g_y1,
                        config.goal_area_radius, side, scale, padding,
                        court_rect_px, line_color.as_bgr(), line_thickness, dashed=False)
        _draw_goal_zone(image, post_x, g_y0, g_y1,
                        config.free_throw_line_distance, side, scale, padding,
                        court_rect_px, line_color.as_bgr(), line_thickness, dashed=True)

    # Goals
    goal_depth_px = int(20 * scale / 10)
    for side in ["left", "right"]:
        if side == "left":
            goal_lower_px = _to_pixel(config.vertices[3], scale, padding)
            goal_upper_px = _to_pixel(config.vertices[2], scale, padding)
            goal_back_x = goal_lower_px[0] - goal_depth_px
            cv2.rectangle(image, (goal_back_x, goal_lower_px[1]),
                          (goal_lower_px[0], goal_upper_px[1]), line_color.as_bgr(), line_thickness)
            cv2.line(image, goal_lower_px, goal_upper_px, line_color.as_bgr(), line_thickness * 2)
        else:
            goal_lower_px = _to_pixel(config.vertices[30], scale, padding)
            goal_upper_px = _to_pixel(config.vertices[29], scale, padding)
            goal_back_x = goal_lower_px[0] + goal_depth_px
            cv2.rectangle(image, (goal_lower_px[0], goal_lower_px[1]),
                          (goal_back_x, goal_upper_px[1]), line_color.as_bgr(), line_thickness)
            cv2.line(image, goal_lower_px, goal_upper_px, line_color.as_bgr(), line_thickness * 2)

    # Substitution area dashes
    half_subst = config.substitution_area_length / 2
    cx = config.court_length / 2
    for court_y in [0, config.court_width]:
        _draw_dashed_line(
            image,
            _to_pixel((cx - half_subst, court_y), scale, padding),
            _to_pixel((cx + half_subst, court_y), scale, padding),
            line_color.as_bgr(), line_thickness, dash_length=15, gap_length=10,
        )

    return image


def draw_made_and_miss_on_court(
    config: CourtConfiguration,
    made_xy: Optional[np.ndarray] = None,
    miss_xy: Optional[np.ndarray] = None,
    made_thickness: Optional[int] = None,
    miss_thickness: Optional[int] = None,
    made_color: sv.Color = sv.Color.from_hex("#007A33"),
    miss_color: sv.Color = sv.Color.from_hex("#850101"),
    made_size: int = 20,
    miss_size: int = 20,
    scale: float = 10,
    padding: int = 50,
    line_thickness: int = 6,
    court: Optional[np.ndarray] = None,
) -> np.ndarray:
    if court is None:
        court = draw_court(config=config, scale=scale, padding=padding, line_thickness=line_thickness)
    made_stroke   = made_thickness if made_thickness is not None else line_thickness
    missed_stroke = miss_thickness if miss_thickness is not None else line_thickness
    made_iter = np.atleast_2d(made_xy) if made_xy is not None and made_xy.size > 0 else ()
    miss_iter = np.atleast_2d(miss_xy) if miss_xy is not None and miss_xy.size > 0 else ()
    for point in made_iter:
        cx, cy = _to_pixel(tuple(point), scale=scale, padding=padding)
        cv2.circle(court, (cx, cy), made_size, made_color.as_bgr(), made_stroke)
    for point in miss_iter:
        cx, cy = _to_pixel(tuple(point), scale=scale, padding=padding)
        cv2.line(court, (cx-miss_size, cy-miss_size), (cx+miss_size, cy+miss_size), miss_color.as_bgr(), missed_stroke)
        cv2.line(court, (cx-miss_size, cy+miss_size), (cx+miss_size, cy-miss_size), miss_color.as_bgr(), missed_stroke)
    return court


def draw_points_on_court(
    config: CourtConfiguration,
    xy: Optional[np.ndarray] = None,
    labels: Optional[list[str]] = None,
    fill_color: Optional[sv.Color] = sv.Color.BLACK,
    text_color: sv.Color = sv.Color.WHITE,
    edge_color: Optional[sv.Color] = sv.Color.WHITE,
    size: int = 30,
    edge_thickness: Optional[int] = None,
    scale: float = 10,
    padding: int = 50,
    line_thickness: int = 6,
    court: Optional[np.ndarray] = None,
) -> np.ndarray:
    if court is None:
        court = draw_court(config=config, scale=scale, padding=padding, line_thickness=line_thickness)
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
        cx, cy = _to_pixel(tuple(pts[i]), scale=scale, padding=padding)
        if fill_color is not None:
            cv2.circle(court, (cx, cy), size, fill_color.as_bgr(), -1, cv2.LINE_AA)
        if edge_color is not None and stroke > 0:
            cv2.circle(court, (cx, cy), size, edge_color.as_bgr(), stroke, cv2.LINE_AA)
        label = labels[i]
        if label is not None and str(label) != "":
            text = str(label)
            (tw, th), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
            cv2.putText(court, text, (int(cx - tw/2), int(cy + th/2)),
                        font, font_scale, text_color.as_bgr(), font_thickness, cv2.LINE_AA)
    return court


def draw_paths_on_court(
    config: CourtConfiguration,
    paths: List[np.ndarray],
    color: Optional[sv.Color] = sv.Color.BLACK,
    thickness: Optional[int] = None,
    scale: float = 10,
    padding: int = 50,
    line_thickness: int = 6,
    court: Optional[np.ndarray] = None,
) -> np.ndarray:
    if court is None:
        court = draw_court(config=config, scale=scale, padding=padding, line_thickness=line_thickness)
    if not paths or color is None:
        return court
    stroke = thickness if thickness is not None else line_thickness
    bgr = color.as_bgr()
    def to_segments(pts):
        pts = np.atleast_2d(pts).astype(float)
        segments, cur = [], []
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
                poly = np.array([[_to_pixel((float(x), float(y)), scale, padding) for x, y in seg]], dtype=np.int32)
                cv2.polylines(court, poly, False, bgr, stroke, cv2.LINE_AA)
            elif seg.shape[0] == 1:
                cx, cy = _to_pixel((float(seg[0,0]), float(seg[0,1])), scale, padding)
                cv2.circle(court, (cx, cy), max(1, stroke//2), bgr, -1, cv2.LINE_AA)
    return court