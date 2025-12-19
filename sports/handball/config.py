from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_CEILING
from enum import Enum
from typing import Dict, List, Tuple

from sports.common.core import MeasurementUnit

CENTIMETERS_PER_FOOT = Decimal("30.48")
CENTIMETERS_PER_METER = Decimal("100")


class League(Enum):
    IHF_INDOOR = "ihf_indoor"  # 40m x 20m


# internal presets in centimeters
HANDBALL_PRESETS_CM: Dict[League, Dict[str, int]] = {
    League.IHF_INDOOR: dict(
        court_length=4000,
        court_width=2000,
        goal_width=300,           # 3m
        goal_center_y=1000,       # centered on width
        # key distances from goal line
        line_4m=400,
        line_6m=600,
        line_7m=700,
        line_9m=900,
        # line segment lengths (approximations for drawing)
        line_7m_segment=100,      # 1m
        line_4m_segment=15,       # 15cm (keeper line)
        # substitution line markers: 4.5m from center line on both sidelines
        substitution_from_center=450,  # 4.5m
    )
}


@dataclass
class CourtConfiguration:
    """
    Handball court (IHF indoor): 40m x 20m.

    Coordinates are (x, y) with:
      - x along court length (0 .. L)
      - y along court width  (0 .. W)

    Origin (0,0) is one corner (choose consistently with your pipeline).
    """
    standard: League = League.IHF_INDOOR
    measurement_unit: MeasurementUnit = MeasurementUnit.CENTIMETERS

    # internal values in centimeters
    _court_length_cm: int = field(init=False)
    _court_width_cm: int = field(init=False)
    _goal_width_cm: int = field(init=False)
    _goal_center_y_cm: int = field(init=False)

    _line_4m_cm: int = field(init=False)
    _line_6m_cm: int = field(init=False)
    _line_7m_cm: int = field(init=False)
    _line_9m_cm: int = field(init=False)

    _line_7m_segment_cm: int = field(init=False)
    _line_4m_segment_cm: int = field(init=False)

    _sub_from_center_cm: int = field(init=False)

    def __post_init__(self) -> None:
        p = HANDBALL_PRESETS_CM[self.standard]
        self._court_length_cm = p["court_length"]
        self._court_width_cm = p["court_width"]
        self._goal_width_cm = p["goal_width"]
        self._goal_center_y_cm = p["goal_center_y"]

        self._line_4m_cm = p["line_4m"]
        self._line_6m_cm = p["line_6m"]
        self._line_7m_cm = p["line_7m"]
        self._line_9m_cm = p["line_9m"]

        self._line_7m_segment_cm = p["line_7m_segment"]
        self._line_4m_segment_cm = p["line_4m_segment"]

        self._sub_from_center_cm = p["substitution_from_center"]

    def _to_output(self, cm: float) -> float:
        v = Decimal(str(cm))
        if self.measurement_unit == MeasurementUnit.FEET:
            v = v / CENTIMETERS_PER_FOOT
        # if you later add meters: v = v / CENTIMETERS_PER_METER
        return float(v.quantize(Decimal("0.01"), rounding=ROUND_CEILING))

    @property
    def court_length(self) -> float:
        return self._to_output(self._court_length_cm)

    @property
    def court_width(self) -> float:
        return self._to_output(self._court_width_cm)

    # ---- vertices / keypoints ----
    def _raw_vertices_cm(self) -> List[Tuple[int, int]]:
        L = self._court_length_cm
        W = self._court_width_cm

        GC = self._goal_center_y_cm
        half_goal = self._goal_width_cm // 2
        GL = GC - half_goal
        GR = GC + half_goal

        x4 = self._line_4m_cm
        x6 = self._line_6m_cm
        x7 = self._line_7m_cm
        x9 = self._line_9m_cm

        # 7m line segment centered on goal center
        y7a = GC - self._line_7m_segment_cm // 2
        y7b = GC + self._line_7m_segment_cm // 2

        # 4m keeper line short segment centered on goal center
        y4a = GC - self._line_4m_segment_cm // 2
        y4b = GC + self._line_4m_segment_cm // 2

        # substitution markers on both sidelines relative to center line
        cx = L // 2
        subL = cx - self._sub_from_center_cm
        subR = cx + self._sub_from_center_cm

        # 9m arc intersections with sidelines:
        # This is a rough-but-useful anchor for broadcasts; keep as “hint” points.
        # Using circle around left goal-post-ish anchor is rule-accurate only as an approximation.
        # You can replace later with proper arc geometry if you need.
        # Here: approximate with x ≈ 296cm from your version.
        x9_sideline = 296
        x9_sideline_r = L - x9_sideline

        return [
            # Court corners (boundary)
            (0, 0),          # 00 bottom-left
            (0, W),          # 01 top-left
            (L, W),          # 02 top-right
            (L, 0),          # 03 bottom-right

            # Center line intersections with sidelines
            (cx, 0),         # 04
            (cx, W),         # 05

            # Left goal posts + center on goal line (x=0)
            (0, GL),         # 06
            (0, GR),         # 07
            (0, GC),         # 08

            # Right goal posts + center (x=L)
            (L, GL),         # 09
            (L, GR),         # 10
            (L, GC),         # 11

            # 6m anchors (straight endpoints across goal width)
            (x6, GL),        # 12
            (x6, GR),        # 13
            (L - x6, GL),    # 14
            (L - x6, GR),    # 15

            # 9m anchors (straight endpoints across goal width)
            (x9, GL),        # 16
            (x9, GR),        # 17
            (L - x9, GL),    # 18
            (L - x9, GR),    # 19

            # 7m penalty line endpoints (1m segment)
            (x7, y7a),       # 20
            (x7, y7b),       # 21
            (L - x7, y7a),   # 22
            (L - x7, y7b),   # 23

            # 4m goalkeeper restraining line endpoints (short segment)
            (x4, y4a),       # 24
            (x4, y4b),       # 25
            (L - x4, y4a),   # 26
            (L - x4, y4b),   # 27

            # Substitution line marks on both sidelines
            (subL, 0),       # 28
            (subR, 0),       # 29
            (subL, W),       # 30
            (subR, W),       # 31

            # optional broadcast-friendly 9m arc hint points
            (x9_sideline, 0),      # 32
            (x9_sideline, W),      # 33
            (x9_sideline_r, 0),    # 34
            (x9_sideline_r, W),    # 35

            # Center spot
            (cx, W // 2),     # 36
        ]

    def _vertices_in_unit(self) -> List[Tuple[float, float]]:
        return [(self._to_output(x), self._to_output(y)) for x, y in self._raw_vertices_cm()]

    @property
    def vertices(self) -> List[Tuple[float, float]]:
        return self._vertices_in_unit()

    labels: List[str] = field(default_factory=lambda: [f"{i:02d}" for i in range(37)])

    edges: List[Tuple[int, int]] = field(default_factory=lambda: [
        # boundary rectangle
        (0, 1), (1, 2), (2, 3), (3, 0),
        # center line
        (4, 5),
        # goal segments (posts)
        (6, 7), (9, 10),
        # 6m straight anchors
        (12, 13), (14, 15),
        # 7m line
        (20, 21), (22, 23),
        # 4m line
        (24, 25), (26, 27),
    ])

    # convenience index getters (same vibe as your basketball class)
    @property
    def court_corner_indexes(self) -> List[int]:
        return [0, 1, 2, 3]

    @property
    def center_line_indexes(self) -> List[int]:
        return [4, 5]

    @property
    def left_goal_post_indexes(self) -> List[int]:
        return [6, 7]

    @property
    def right_goal_post_indexes(self) -> List[int]:
        return [9, 10]

    @property
    def center_spot_index(self) -> int:
        return 36