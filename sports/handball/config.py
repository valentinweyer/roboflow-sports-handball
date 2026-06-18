from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_CEILING
from enum import Enum
from typing import Dict, List, Tuple

from sports.common.core import MeasurementUnit

CENTIMETERS_PER_FOOT = Decimal("30.48")


class League(Enum):
    IHF = "ihf"  # International Handball Federation


# presets stored in centimeters
PRESETS_CENTIMETERS: Dict[League, Dict[str, int]] = {
    League.IHF: dict(
        court_width=2000,  # 20 meters
        court_length=4000,  # 40 meters
        goal_area_radius=600,  # 6 meter line (semicircular arc)
        penalty_spot_distance=700,  # 7 meter penalty line
        free_throw_line_distance=900,  # 9 meter free throw line
        goal_width=300,  # 3 meters
        goal_height=200,  # 2 meters (not used in 2D court rendering)
        goal_area_width=300,  # Width of goal (same as goal_width)
        center_circle_radius=180,  # Center circle radius
        substitution_area_length=450,  # 4.5 meters substitution zone
        goalkeeper_restraining_line=400,  # 4 meter line
    ),
}


@dataclass
class CourtConfiguration:
    """Configure handball court dimensions for IHF league standard.
    Provides court measurements in centimeters or feet with proper unit
    conversion and vertex/edge data for court visualization.

    Args:
        league: The handball league standard to use (`League.IHF`).
        measurement_unit: Output unit for measurements
            (`MeasurementUnit.CENTIMETERS` or `MeasurementUnit.FEET`).

    Examples:
        ```
        from sports import MeasurementUnit
        from sports.handball import CourtConfiguration, League

        # Create IHF court configuration in centimeters
        ihf_config = CourtConfiguration(
            league=League.IHF,
            measurement_unit=MeasurementUnit.CENTIMETERS
        )
        print(f"Court width: {ihf_config.court_width} cm")
        # Court width: 2000.0 cm
        print(f"Goal area radius: {ihf_config.goal_area_radius} cm")
        # Goal area radius: 600.0 cm
        ```
    """
    league: League
    measurement_unit: MeasurementUnit = MeasurementUnit.CENTIMETERS

    # internal values in centimeters
    _court_width_in_centimeters: int = field(init=False)
    _court_length_in_centimeters: int = field(init=False)
    _goal_area_radius_in_centimeters: int = field(init=False)
    _penalty_spot_distance_in_centimeters: int = field(init=False)
    _free_throw_line_distance_in_centimeters: int = field(init=False)
    _goal_width_in_centimeters: int = field(init=False)
    _goal_height_in_centimeters: int = field(init=False)
    _goal_area_width_in_centimeters: int = field(init=False)
    _center_circle_radius_in_centimeters: int = field(init=False)
    _substitution_area_length_in_centimeters: int = field(init=False)
    _goalkeeper_restraining_line_in_centimeters: int = field(init=False)

    def __post_init__(self) -> None:
        preset = PRESETS_CENTIMETERS[self.league]
        self._court_width_in_centimeters = preset["court_width"]
        self._court_length_in_centimeters = preset["court_length"]
        self._goal_area_radius_in_centimeters = preset["goal_area_radius"]
        self._penalty_spot_distance_in_centimeters = preset["penalty_spot_distance"]
        self._free_throw_line_distance_in_centimeters = preset["free_throw_line_distance"]
        self._goal_width_in_centimeters = preset["goal_width"]
        self._goal_height_in_centimeters = preset["goal_height"]
        self._goal_area_width_in_centimeters = preset["goal_area_width"]
        self._center_circle_radius_in_centimeters = preset["center_circle_radius"]
        self._substitution_area_length_in_centimeters = preset["substitution_area_length"]
        self._goalkeeper_restraining_line_in_centimeters = preset["goalkeeper_restraining_line"]

    # conversion helpers
    def _to_output_unit_rounded_up(self, value_in_centimeters: float) -> float:
        value = Decimal(str(value_in_centimeters))
        if self.measurement_unit == MeasurementUnit.FEET:
            value = value / CENTIMETERS_PER_FOOT
        return float(value.quantize(Decimal("0.01"), rounding=ROUND_CEILING))

    # public properties in the selected unit
    @property
    def court_width(self) -> float:
        """Get the court width in the configured measurement unit.

        Returns:
            `float`: Court width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._court_width_in_centimeters)

    @property
    def court_length(self) -> float:
        """Get the court length in the configured measurement unit.

        Returns:
            `float`: Court length in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._court_length_in_centimeters)

    @property
    def goal_area_radius(self) -> float:
        """Get the goal area radius (6m line) in the configured measurement unit.

        Returns:
            `float`: Goal area radius in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._goal_area_radius_in_centimeters
        )

    @property
    def penalty_spot_distance(self) -> float:
        """Get the penalty spot distance (7m line) from goal line.

        Returns:
            `float`: Penalty spot distance in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._penalty_spot_distance_in_centimeters
        )

    @property
    def free_throw_line_distance(self) -> float:
        """Get the free throw line distance (9m line) from goal line.

        Returns:
            `float`: Free throw line distance in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._free_throw_line_distance_in_centimeters
        )

    @property
    def goal_width(self) -> float:
        """Get the goal width in the configured measurement unit.

        Returns:
            `float`: Goal width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._goal_width_in_centimeters)

    @property
    def goal_height(self) -> float:
        """Get the goal height in the configured measurement unit.

        Returns:
            `float`: Goal height in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._goal_height_in_centimeters)

    @property
    def goal_area_width(self) -> float:
        """Get the goal area width in the configured measurement unit.

        Returns:
            `float`: Goal area width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._goal_area_width_in_centimeters)

    @property
    def center_circle_radius(self) -> float:
        """Get the center circle radius in the configured measurement unit.

        Returns:
            `float`: Center circle radius in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._center_circle_radius_in_centimeters
        )

    @property
    def substitution_area_length(self) -> float:
        """Get the substitution area length in the configured measurement unit.

        Returns:
            `float`: Substitution area length in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._substitution_area_length_in_centimeters
        )

    @property
    def goalkeeper_restraining_line(self) -> float:
        """Get the goalkeeper restraining line distance (4m line).

        Returns:
            `float`: Goalkeeper restraining line distance in centimeters or feet
                based on `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._goalkeeper_restraining_line_in_centimeters
        )

    # internals for geometry in centimeters
    @property
    def _goal_start_in_centimeters(self) -> int:
        """Calculate where the goal starts on the width axis (centered)."""
        return (
            self._court_width_in_centimeters - self._goal_width_in_centimeters
        ) // 2

    def _raw_vertices_centimeters(self) -> List[Tuple[int, int]]:
        """Generate vertices for handball court in centimeters.
        37 keypoints matching the model output (indices 0-36 for keypoints 01-37).
        """
        goal_start = self._goal_start_in_centimeters
        goal_end = goal_start + self._goal_width_in_centimeters
        middle_court_width = self._court_width_in_centimeters // 2
        court_width = self._court_width_in_centimeters
        court_length = self._court_length_in_centimeters
        half_length = court_length // 2

        return [
            # LEFT SIDE (Purple keypoints 01-13, indices 0-12)
            (0, court_width),  # 0 (KP 01): Top left corner
            (0, goal_end + self._goal_area_radius_in_centimeters),  # 1 (KP 02): Left upper 6m/goal-line intersection
            (0, goal_end),  # 2 (KP 03): Left side upper goal post
            (0, goal_start),  # 3 (KP 04): Left side lower goal post
            (0, goal_start - self._goal_area_radius_in_centimeters),  # 4 (KP 05): Left lower 6m/goal-line intersection
            (0, 0),  # 5 (KP 06): Bottom left corner
            # KP07/KP10: where the 9m arc meets the sideline.
            # Arc centred at upper post (0, goal_end): x = sqrt(r9²-(court_width-goal_end)²)
            # Arc centred at lower post (0, goal_start): x = sqrt(r9²-goal_start²)
            (int(round((self._free_throw_line_distance_in_centimeters**2 - (court_width - goal_end)**2)**0.5)), court_width),  # 6 (KP 07): Left top 9m/sideline intersection
            (self._goal_area_radius_in_centimeters, goal_end),  # 7 (KP 08): Left 6m upper tangent point
            (self._goal_area_radius_in_centimeters, goal_start),  # 8 (KP 09): Left 6m lower tangent point
            (int(round((self._free_throw_line_distance_in_centimeters**2 - goal_start**2)**0.5)), 0),  # 9 (KP 10): Left bottom 9m/sideline intersection
            (self._goal_area_radius_in_centimeters, middle_court_width),  # 10 (KP 11): Left 6m straight midpoint
            (self._penalty_spot_distance_in_centimeters, middle_court_width + 50),  # 11 (KP 12): Left 7m line upper point
            (self._penalty_spot_distance_in_centimeters, middle_court_width - 50),  # 12 (KP 13): Left 7m line lower point

            # CENTER SECTION (White keypoints 14-20, indices 13-19)
            (half_length, court_width),  # 13 (KP 14): Top center
            (half_length, goal_end),  # 14 (KP 15): Center mid-upper
            (half_length - self._center_circle_radius_in_centimeters, middle_court_width),  # 15 (KP 16): Center left point
            (half_length, middle_court_width),  # 16 (KP 17): Center point
            (half_length + self._center_circle_radius_in_centimeters, middle_court_width),  # 17 (KP 18): Center right point
            (half_length, goal_start),  # 18 (KP 19): Center mid-lower
            (half_length, 0),  # 19 (KP 20): Bottom center

            # RIGHT SIDE (Orange keypoints 21-33, indices 20-32)
            (court_length - self._penalty_spot_distance_in_centimeters, middle_court_width + 50),  # 20 (KP 21): Right 7m line upper point
            (court_length - self._penalty_spot_distance_in_centimeters, middle_court_width - 50),  # 21 (KP 22): Right 7m line lower point
            (court_length - self._goal_area_radius_in_centimeters, middle_court_width),  # 22 (KP 23): Right 6m straight midpoint
            (court_length - int(round((self._free_throw_line_distance_in_centimeters**2 - (court_width - goal_end)**2)**0.5)), court_width),  # 23 (KP 24): Right top 9m/sideline intersection
            (court_length - self._goal_area_radius_in_centimeters, goal_end),  # 24 (KP 25): Right 6m upper tangent point
            (court_length - self._goal_area_radius_in_centimeters, goal_start),  # 25 (KP 26): Right 6m lower tangent point
            (court_length - int(round((self._free_throw_line_distance_in_centimeters**2 - goal_start**2)**0.5)), 0),  # 26 (KP 27): Right bottom 9m/sideline intersection
            (court_length, court_width),  # 27 (KP 28): Top right corner
            (court_length, goal_end + self._goal_area_radius_in_centimeters),  # 28 (KP 29): Right upper 6m/goal-line intersection
            (court_length, goal_end),  # 29 (KP 30): Right side upper goal post
            (court_length, goal_start),  # 30 (KP 31): Right side lower goal post
            (court_length, goal_start - self._goal_area_radius_in_centimeters),  # 31 (KP 32): Right lower 6m/goal-line intersection
            (court_length, 0),  # 32 (KP 33): Bottom right corner

            # CENTER SECTION CONTINUED (White keypoints 34-37, indices 33-36)
            (self._free_throw_line_distance_in_centimeters, goal_end),  # 33 (KP 34): Left 9m upper tangent point
            (self._free_throw_line_distance_in_centimeters, goal_start),  # 34 (KP 35): Left 9m lower tangent point
            (court_length - self._free_throw_line_distance_in_centimeters, goal_end),  # 35 (KP 36): Right 9m upper tangent point
            (court_length - self._free_throw_line_distance_in_centimeters, goal_start),  # 36 (KP 37): Right 9m lower tangent point
        ]

    def _vertices_in_unit(self) -> List[Tuple[float, float]]:
        return [
            (
                self._to_output_unit_rounded_up(x),
                self._to_output_unit_rounded_up(y),
            )
            for x, y in self._raw_vertices_centimeters()
        ]

    @property
    def vertices(self) -> List[Tuple[float, float]]:
        """Get all court vertices in the configured measurement unit.
        Returns a list of coordinate pairs representing key points on the
        handball court for geometry calculations and visualization.

        Returns:
            `List[Tuple[float, float]]`: List of (x, y) coordinate pairs
                in centimeters or feet based on `measurement_unit` setting.
        """
        return self._vertices_in_unit()

    edges: List[Tuple[int, int]] = field(default_factory=lambda: [
        # Outer court boundaries
        (0, 5),   # Left baseline          KP01 → KP06
        (5, 19),  # Bottom baseline        KP06 → KP20
        (19, 32), # Right baseline (bot)   KP20 → KP33
        (32, 27), # Right baseline (top)   KP33 → KP28
        (27, 13), # Top baseline           KP28 → KP14
        (13, 0),  # Top baseline (left)    KP14 → KP01

        # Center line
        (13, 19), # KP14 → KP20

        # Goal lines (6m intersection → upper post → lower post → 6m intersection)
        (1, 2),   # Left  KP02 → KP03
        (2, 3),   # Left  KP03 → KP04
        (3, 4),   # Left  KP04 → KP05
        (28, 29), # Right KP29 → KP30
        (29, 30), # Right KP30 → KP31
        (30, 31), # Right KP31 → KP32

        # 6m straight segments (between tangent points, parallel to goal line)
        (7, 8),   # Left  KP08 → KP09
        (24, 25), # Right KP25 → KP26

        # 9m straight segments
        (33, 34), # Left  KP34 → KP35
        (35, 36), # Right KP36 → KP37

        # 7m lines
        (11, 12), # Left  KP12 → KP13
        (20, 21), # Right KP21 → KP22
    ])

    labels: List[str] = field(default_factory=lambda: [
        # LEFT SIDE (Purple keypoints 01-13, indices 0-12)
        "KP01-TL-Corner",         # 0 (KP 01): Top left corner
        "KP02-L-Upper-6m",        # 1 (KP 02): Left side upper 6m goal line intersection
        "KP03-L-Upper-Goal",      # 2 (KP 03): Left side upper goal post
        "KP04-L-Lower-Goal",      # 3 (KP 04): Left side lower goal post
        "KP05-L-Lower-6m",        # 4 (KP 05): Left side lower 6m goal line intersection
        "KP06-BL-Corner",         # 5 (KP 06): Bottom left corner
        "KP07-L-Top-9m",          # 6 (KP 07): Left top 9m out line intersection
        "KP08-L-6m-Upper",        # 7 (KP 08): Left 6m area upper point
        "KP09-L-6m-Lower",        # 8 (KP 09): Left 6m area lower point
        "KP10-L-Bottom-9m",       # 9 (KP 10): Left lower 9m out line intersection
        "KP11-L-6m-Center",       # 10 (KP 11): Left side interior point (6m center)
        "KP12-L-7m-Upper",        # 11 (KP 12): Left 7m line upper point
        "KP13-L-7m-Lower",        # 12 (KP 13): Left 7m line lower point
        
        # CENTER SECTION (White keypoints 14-20, indices 13-19)
        "KP14-Top-Center",        # 13 (KP 14): Top center
        "KP15-Center-Mid-Upper",  # 14 (KP 15): Center mid-upper
        "KP16-Center-Left",       # 15 (KP 16): Center left point
        "KP17-Center",            # 16 (KP 17): Center point
        "KP18-Center-Right",      # 17 (KP 18): Center right point
        "KP19-Center-Mid-Lower",  # 18 (KP 19): Center mid-lower
        "KP20-Bottom-Center",     # 19 (KP 20): Bottom center
        
        # RIGHT SIDE (Orange keypoints 21-33, indices 20-32)
        "KP21-R-7m-Upper",        # 20 (KP 21): Right 7m line upper point
        "KP22-R-7m-Lower",        # 21 (KP 22): Right 7m line lower point
        "KP23-R-6m-Center",       # 22 (KP 23): Right side interior point (6m center)
        "KP24-R-Top-9m",          # 23 (KP 24): Right top 9m out line intersection
        "KP25-R-6m-Upper",        # 24 (KP 25): Right 6m area upper point
        "KP26-R-6m-Lower",        # 25 (KP 26): Right 6m area lower point
        "KP27-R-Bottom-9m",       # 26 (KP 27): Right lower 9m out line intersection
        "KP28-TR-Corner",         # 27 (KP 28): Top right corner
        "KP29-R-Upper-6m",        # 28 (KP 29): Right side upper 6m goal line intersection
        "KP30-R-Upper-Goal",      # 29 (KP 30): Right side upper goal post
        "KP31-R-Lower-Goal",      # 30 (KP 31): Right side lower goal post
        "KP32-R-Lower-6m",        # 31 (KP 32): Right side lower 6m goal line intersection
        "KP33-BR-Corner",         # 32 (KP 33): Bottom right corner
        
        # CENTER SECTION CONTINUED (White keypoints 34-37, indices 33-36)
        "KP34-L-9m-Upper",        # 33 (KP 34): Left 9m area upper point
        "KP35-L-9m-Lower",        # 34 (KP 35): Left 9m area lower point
        "KP36-R-9m-Upper",        # 35 (KP 36): Right 9m area upper point
        "KP37-R-9m-Lower",        # 36 (KP 37): Right 9m area lower point
    ])

    colors: List[str] = field(default_factory=lambda: [
        # LEFT SIDE (Purple keypoints 01-13, indices 0-12)
        "#9B59B6", "#9B59B6", "#9B59B6", "#9B59B6", "#9B59B6",  # 0-4: Purple
        "#9B59B6", "#9B59B6", "#9B59B6", "#9B59B6", "#9B59B6",  # 5-9: Purple
        "#9B59B6", "#9B59B6", "#9B59B6",                        # 10-12: Purple
        
        # CENTER SECTION (White keypoints 14-20, indices 13-19)
        "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",  # 13-17: White
        "#FFFFFF", "#FFFFFF",                                   # 18-19: White
        
        # RIGHT SIDE (Orange keypoints 21-33, indices 20-32)
        "#FF8C00", "#FF8C00", "#FF8C00", "#FF8C00", "#FF8C00",  # 20-24: Orange
        "#FF8C00", "#FF8C00", "#FF8C00", "#FF8C00", "#FF8C00",  # 25-29: Orange
        "#FF8C00", "#FF8C00", "#FF8C00",                        # 30-32: Orange
        
        # CENTER SECTION CONTINUED (White keypoints 34-37, indices 33-36)
        "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",             # 33-36: White
    ])

    # Direct index getters
    @property
    def left_goal_area_indexes(self) -> List[int]:
        """Get vertex indexes defining the left goal area (6m line).
        
        Returns:
            `List[int]`: List of vertex indexes for left goal area.
        """
        return [4, 8, 10, 7, 1]  # KP 05, 09, 11, 08, 02

    @property
    def right_goal_area_indexes(self) -> List[int]:
        """Get vertex indexes defining the right goal area (6m line).
        
        Returns:
            `List[int]`: List of vertex indexes for right goal area.
        """
        return [31, 25, 22, 24, 28]  # KP 32, 26, 23, 25, 29

    @property
    def left_goal_index(self) -> int:
        """Get vertex index for the left goal center position.
        
        Returns:
            `int`: Vertex index for left goal center coordinates.
        """
        return 10  # KP 11 - Left 6m center point (kept for backward compatibility)

    @property
    def right_goal_index(self) -> int:
        """Get vertex index for the right goal center position.
        
        Returns:
            `int`: Vertex index for right goal center coordinates.
        """
        return 22  # KP 23 - Right 6m center point (kept for backward compatibility)

    @property
    def left_goal_center(self) -> Tuple[float, float]:
        """Get left goal center computed from goal post keypoints.

        Returns:
            `Tuple[float, float]`: (x, y) coordinates of left goal center.
        """
        upper = self.vertices[2]  # KP 03
        lower = self.vertices[3]  # KP 04
        return (upper[0], (upper[1] + lower[1]) / 2.0)

    @property
    def right_goal_center(self) -> Tuple[float, float]:
        """Get right goal center computed from goal post keypoints.

        Returns:
            `Tuple[float, float]`: (x, y) coordinates of right goal center.
        """
        upper = self.vertices[29]  # KP 30
        lower = self.vertices[30]  # KP 31
        return (upper[0], (upper[1] + lower[1]) / 2.0)

    @property
    def court_corner_indexes(self) -> List[int]:
        """Get vertex indexes for the four court corners.
        
        Returns:
            `List[int]`: List of vertex indexes for court corners in order:
                bottom-left, top-left, top-right, bottom-right.
        """
        return [5, 0, 27, 32]  # KP 06, 01, 28, 33

    @property
    def left_penalty_spot_index(self) -> int:
        """Get vertex index for the left penalty spot (7m line center).
        
        Returns:
            `int`: Vertex index for left penalty spot.
        """
        return 11  # KP 12 - Left 7m line upper point (or could use 12 for lower)

    @property
    def right_penalty_spot_index(self) -> int:
        """Get vertex index for the right penalty spot (7m line center).
        
        Returns:
            `int`: Vertex index for right penalty spot.
        """
        return 20  # KP 21 - Right 7m line upper point (or could use 21 for lower)

    @property
    def left_penalty_spot(self) -> Tuple[float, float]:
        """Get left penalty spot center from 7m line endpoints."""
        upper = self.vertices[11]  # KP 12
        lower = self.vertices[12]  # KP 13
        return (upper[0], (upper[1] + lower[1]) / 2.0)

    @property
    def right_penalty_spot(self) -> Tuple[float, float]:
        """Get right penalty spot center from 7m line endpoints."""
        upper = self.vertices[20]  # KP 21
        lower = self.vertices[21]  # KP 22
        return (upper[0], (upper[1] + lower[1]) / 2.0)
    
    @property
    def center_point_index(self) -> int:
        """Get vertex index for the center point of the court.
        
        Returns:
            `int`: Vertex index for center point.
        """
        return 16  # KP 17 - Center point