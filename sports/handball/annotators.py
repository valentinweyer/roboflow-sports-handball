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
) -> Tuple[int, int]:
    """Scale court point to pixel space and apply padding."""
    return (
        int(round(point[0] * scale + padding)),
        int(round(point[1] * scale + padding)),
    )


def _draw_circular_arc_from_three_points(
    image: np.ndarray,
    first_point: Tuple[float, float],
    middle_point: Tuple[float, float],
    last_point: Tuple[float, float],
    bgr_color: Tuple[int, int, int],
    thickness: int,
) -> None:
    """Draw an arc defined by three points."""
    def circle_from_three_points(
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
    ):
        sum_sq_p2 = p2[0] ** 2 + p2[1] ** 2
        term1 = (p1[0] ** 2 + p1[1] ** 2 - sum_sq_p2) / 2.0
        term2 = (sum_sq_p2 - p3[0] ** 2 - p3[1] ** 2) / 2.0
        det = (
            (p1[0] - p2[0]) * (p2[1] - p3[1])
            - (p2[0] - p3[0]) * (p1[1] - p2[1])
        )
        if abs(det) < 1e-10:
            return (p2, 0.0)
        center_x = (term1 * (p2[1] - p3[1]) - term2 * (p1[1] - p2[1])) / det
        center_y = (
            (p1[0] - p2[0]) * term2 - (p2[0] - p3[0]) * term1
        ) / det
        radius = float(np.hypot(center_x - p1[0], center_y - p1[1]))
        return (center_x, center_y), radius

    def angle_deg(center_xy, point_xy) -> float:
        return float(
            np.degrees(
                np.arctan2(point_xy[1] - center_xy[1], point_xy[0] - center_xy[0])
            )
        )

    center, radius = circle_from_three_points(
        first_point, middle_point, last_point
    )
    center_px = (int(round(center[0])), int(round(center[1])))
    radius_px = int(round(radius))

    start_angle = angle_deg(center, first_point)
    end_angle = angle_deg(center, last_point)
    if end_angle < start_angle:
        end_angle += 360.0

    cv2.ellipse(
        image,
        center=center_px,
        axes=(radius_px, radius_px),
        angle=0,
        startAngle=int(round(start_angle)),
        endAngle=int(round(end_angle)),
        color=bgr_color,
        thickness=thickness,
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
    """Draw a dashed line between two points."""
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = np.sqrt(dx * dx + dy * dy)
    
    if distance < 1:
        return
    
    # Normalize direction
    dx /= distance
    dy /= distance
    
    current_dist = 0
    while current_dist < distance:
        dash_start_x = int(start[0] + dx * current_dist)
        dash_start_y = int(start[1] + dy * current_dist)
        
        dash_end_dist = min(current_dist + dash_length, distance)
        dash_end_x = int(start[0] + dx * dash_end_dist)
        dash_end_y = int(start[1] + dy * dash_end_dist)
        
        cv2.line(image, (dash_start_x, dash_start_y), (dash_end_x, dash_end_y),
                bgr_color, thickness)
        
        current_dist += dash_length + gap_length


def draw_court(
    config: CourtConfiguration,
    scale: float = 10,
    padding: int = 50,
    line_thickness: int = 4,
    line_color: sv.Color = sv.Color.WHITE,
    background_color: sv.Color = sv.Color(200, 160, 120),
    goal_area_color: Optional[sv.Color] = None,
) -> np.ndarray:
    """Render a handball court to an image.
    
    Args:
        config: Court configuration with dimensions
        scale: Scaling factor for court dimensions to pixels
        padding: Padding around the court in pixels
        line_thickness: Thickness of court lines
        line_color: Color of court lines
        background_color: Color of court background
        goal_area_color: Optional fill color for goal areas (6m zones)
    
    Returns:
        np.ndarray: Rendered court image
    """
    court_height_px = int(round(config.court_width * scale))
    court_length_px = int(round(config.court_length * scale))
    center_circle_radius_px = int(round(config.center_circle_radius * scale))
    goal_area_radius_px = int(round(config.goal_area_radius * scale))
    free_throw_radius_px = int(round(config.free_throw_line_distance * scale))

    image = np.zeros(
        (court_height_px + 2 * padding, court_length_px + 2 * padding, 3),
        dtype=np.uint8,
    )
    image[:, :] = background_color.as_bgr()

    # Fill goal areas if color is specified
    if goal_area_color is not None:
        # Left goal area
        left_goal_center = _to_pixel(config.left_goal_center, scale, padding)
        cv2.ellipse(
            image,
            center=left_goal_center,
            axes=(goal_area_radius_px, goal_area_radius_px),
            angle=90,
            startAngle=180,
            endAngle=360,
            color=goal_area_color.as_bgr(),
            thickness=-1,  # Filled
        )
        
        # Right goal area
        right_goal_center = _to_pixel(config.right_goal_center, scale, padding)
        cv2.ellipse(
            image,
            center=right_goal_center,
            axes=(goal_area_radius_px, goal_area_radius_px),
            angle=90,
            startAngle=0,
            endAngle=180,
            color=goal_area_color.as_bgr(),
            thickness=-1,  # Filled
        )

    # Draw court boundary edges
    for start_idx, end_idx in config.edges:
        start_px = _to_pixel(config.vertices[start_idx], scale, padding)
        end_px = _to_pixel(config.vertices[end_idx], scale, padding)
        cv2.line(image, start_px, end_px, line_color.as_bgr(), line_thickness)

    # Draw center circle
    center_px = _to_pixel(config.vertices[16], scale, padding)  # KP 17 - Center point
    cv2.circle(
        image,
        center_px,
        center_circle_radius_px,
        line_color.as_bgr(),
        line_thickness,
    )

    # Draw goal area arcs (6m lines) for both sides
    for side in ["left", "right"]:
        goal_center = (
            config.left_goal_center if side == "left" else config.right_goal_center
        )
        goal_px = _to_pixel(goal_center, scale, padding)
        
        # Draw semicircular arc for goal area
        start_ang, end_ang = ((180, 360) if side == "left" else (0, 180))
        cv2.ellipse(
            image,
            center=goal_px,
            axes=(goal_area_radius_px, goal_area_radius_px),
            angle=90,
            startAngle=start_ang,
            endAngle=end_ang,
            color=line_color.as_bgr(),
            thickness=line_thickness,
        )
        
        # Draw 9m free throw line arcs (concentric with 6m goal area arcs)
        cv2.ellipse(
            image,
            center=goal_px,
            axes=(free_throw_radius_px, free_throw_radius_px),
            angle=90,
            startAngle=start_ang,
            endAngle=end_ang,
            color=line_color.as_bgr(),
            thickness=line_thickness,
        )
        
        # Draw penalty spot (7m line)
        penalty_pt = (
            config.left_penalty_spot if side == "left" else config.right_penalty_spot
        )
        penalty_px = _to_pixel(penalty_pt, scale, padding)
        cv2.circle(
            image,
            penalty_px,
            max(3, line_thickness),
            line_color.as_bgr(),
            -1,  # Filled circle
        )

    # Draw goals (as rectangles at the court ends)
    goal_depth_px = int(20 * scale / 10)  # Goal depth for visualization
    for side in ["left", "right"]:
        if side == "left":
            # Left goal: KP 04 (index 3) lower post, KP 03 (index 2) upper post
            goal_lower_px = _to_pixel(config.vertices[3], scale, padding)
            goal_upper_px = _to_pixel(config.vertices[2], scale, padding)
            goal_back_x = goal_lower_px[0] - goal_depth_px
            
            # Draw goal rectangle
            cv2.rectangle(
                image,
                (goal_back_x, goal_lower_px[1]),
                (goal_lower_px[0], goal_upper_px[1]),
                line_color.as_bgr(),
                line_thickness,
            )
            # Draw goal posts (thicker)
            cv2.line(image, goal_lower_px, goal_upper_px, line_color.as_bgr(), line_thickness * 2)
        else:
            # Right goal: KP 31 (index 30) lower post, KP 30 (index 29) upper post
            goal_lower_px = _to_pixel(config.vertices[30], scale, padding)
            goal_upper_px = _to_pixel(config.vertices[29], scale, padding)
            goal_back_x = goal_lower_px[0] + goal_depth_px
            
            # Draw goal rectangle
            cv2.rectangle(
                image,
                (goal_lower_px[0], goal_lower_px[1]),
                (goal_back_x, goal_upper_px[1]),
                line_color.as_bgr(),
                line_thickness,
            )
            # Draw goal posts (thicker)
            cv2.line(image, goal_lower_px, goal_upper_px, line_color.as_bgr(), line_thickness * 2)

    # Draw substitution areas (dashed lines along center line)
    subst_length = config.substitution_area_length
    half_subst = subst_length / 2
    center_x = config.court_length / 2
    center_y = config.court_width / 2
    
    # Left side substitution area (bottom)
    subst_start_left = _to_pixel((center_x - half_subst, 0), scale, padding)
    subst_end_left = _to_pixel((center_x + half_subst, 0), scale, padding)
    _draw_dashed_line(image, subst_start_left, subst_end_left, 
                     line_color.as_bgr(), line_thickness, dash_length=15, gap_length=10)
    
    # Right side substitution area (top)
    subst_start_right = _to_pixel((center_x - half_subst, config.court_width), scale, padding)
    subst_end_right = _to_pixel((center_x + half_subst, config.court_width), scale, padding)
    _draw_dashed_line(image, subst_start_right, subst_end_right,
                     line_color.as_bgr(), line_thickness, dash_length=15, gap_length=10)

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
    """Draw made goals as circle outlines and missed shots as crosses.
    
    Args:
        config: Court configuration
        made_xy: Array of (x, y) coordinates for made goals
        miss_xy: Array of (x, y) coordinates for missed shots
        made_thickness: Line thickness for made goal markers
        miss_thickness: Line thickness for missed shot markers
        made_color: Color for made goal markers
        miss_color: Color for missed shot markers
        made_size: Radius of made goal circles
        miss_size: Size of missed shot crosses
        scale: Scaling factor
        padding: Padding around court
        line_thickness: Court line thickness
        court: Optional pre-rendered court image
    
    Returns:
        np.ndarray: Court image with markers
    """
    if court is None:
        court = draw_court(
            config=config,
            scale=scale,
            padding=padding,
            line_thickness=line_thickness,
        )

    made_stroke = (
        made_thickness if made_thickness is not None else line_thickness
    )
    missed_stroke = (
        miss_thickness if miss_thickness is not None else line_thickness
    )

    def point_to_pixel(point: Tuple[float, float]) -> Tuple[int, int]:
        return _to_pixel(point, scale=scale, padding=padding)

    # Normalize inputs to iterable collections
    made_iter = (
        np.atleast_2d(made_xy) if made_xy is not None and made_xy.size > 0 else ()
    )
    miss_iter = (
        np.atleast_2d(miss_xy) if miss_xy is not None and miss_xy.size > 0 else ()
    )

    # Made goals: circle border
    for point in made_iter:
        center_x, center_y = point_to_pixel(tuple(point))
        cv2.circle(
            img=court,
            center=(center_x, center_y),
            radius=made_size,
            color=made_color.as_bgr(),
            thickness=made_stroke,
        )

    # Missed shots: cross
    for point in miss_iter:
        center_x, center_y = point_to_pixel(tuple(point))
        x0, y0 = center_x - miss_size, center_y - miss_size
        x1, y1 = center_x + miss_size, center_y + miss_size
        cv2.line(court, (x0, y0), (x1, y1), miss_color.as_bgr(), missed_stroke)
        cv2.line(court, (x0, y1), (x1, y0), miss_color.as_bgr(), missed_stroke)

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
    """
    Draw points on the court.
    Points render as circles with optional fill, edge, and center labels.
    
    Args:
        config: Court configuration
        xy: Array of (x, y) coordinates to draw
        labels: Optional labels for each point
        fill_color: Fill color for circles
        text_color: Color for text labels
        edge_color: Color for circle edges
        size: Radius of circles
        edge_thickness: Thickness of circle edges
        scale: Scaling factor
        padding: Padding around court
        line_thickness: Court line thickness
        court: Optional pre-rendered court image
    
    Returns:
        np.ndarray: Court image with points
    """
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
        cx, cy = _to_pixel(tuple(pts[i]), scale=scale, padding=padding)

        # Face (fill)
        if fill_color is not None:
            cv2.circle(
                img=court,
                center=(cx, cy),
                radius=size,
                color=fill_color.as_bgr(),
                thickness=-1,
                lineType=cv2.LINE_AA,
            )

        # Edge (outline)
        if edge_color is not None and stroke > 0:
            cv2.circle(
                img=court,
                center=(cx, cy),
                radius=size,
                color=edge_color.as_bgr(),
                thickness=stroke,
                lineType=cv2.LINE_AA,
            )

        # Label
        label = labels[i]
        if label is not None and str(label) != "":
            text = str(label)
            (tw, th), base = cv2.getTextSize(text, font, font_scale, font_thickness)
            tx = int(cx - tw / 2)
            ty = int(cy + th / 2)
            cv2.putText(
                img=court,
                text=text,
                org=(tx, ty),
                fontFace=font,
                fontScale=font_scale,
                color=text_color.as_bgr(),
                thickness=font_thickness,
                lineType=cv2.LINE_AA,
            )

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
    """
    Draw time-ordered paths as polylines in court coordinates.
    Each path is an array of shape (T, 2) with x, y in court units.
    NaN rows split a path into multiple segments.
    
    Args:
        config: Court configuration
        paths: List of path arrays, each shape (T, 2)
        color: Color for path lines
        thickness: Line thickness for paths
        scale: Scaling factor
        padding: Padding around court
        line_thickness: Court line thickness
        court: Optional pre-rendered court image
    
    Returns:
        np.ndarray: Court image with paths
    """
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
        segments = []
        cur = []
        for p in pts:
            if np.isnan(p).any():
                if len(cur) > 0:
                    segments.append(np.asarray(cur, dtype=float))
                    cur = []
            else:
                cur.append(p)
        if len(cur) > 0:
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
