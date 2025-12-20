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
        """Generate vertices for handball court in centimeters."""
        goal_start = self._goal_start_in_centimeters
        middle_court_width = self._court_width_in_centimeters // 2
        court_width = self._court_width_in_centimeters
        court_length = self._court_length_in_centimeters
        half_length = court_length // 2

        return [
            # Corner vertices
            (0, 0),  # 0: Left baseline, bottom corner
            (0, court_width),  # 1: Left baseline, top corner
            (court_length, 0),  # 2: Right baseline, bottom corner
            (court_length, court_width),  # 3: Right baseline, top corner
            
            # Goal line vertices (left side)
            (0, goal_start),  # 4: Left goal, bottom post
            (0, goal_start + self._goal_width_in_centimeters),  # 5: Left goal, top post
            (0, middle_court_width),  # 6: Left goal center
            
            # Goal line vertices (right side)
            (court_length, goal_start),  # 7: Right goal, bottom post
            (court_length, goal_start + self._goal_width_in_centimeters),  # 8: Right goal, top post
            (court_length, middle_court_width),  # 9: Right goal center
            
            # Center line
            (half_length, 0),  # 10: Center line, bottom
            (half_length, court_width),  # 11: Center line, top
            (half_length, middle_court_width),  # 12: Center point
            
            # Left side key points for 6m line arc
            (self._goal_area_radius_in_centimeters, goal_start),  # 13: Left 6m arc, bottom
            (self._goal_area_radius_in_centimeters, middle_court_width),  # 14: Left 6m arc, center
            (self._goal_area_radius_in_centimeters, goal_start + self._goal_width_in_centimeters),  # 15: Left 6m arc, top
            
            # Right side key points for 6m line arc
            (court_length - self._goal_area_radius_in_centimeters, goal_start),  # 16: Right 6m arc, bottom
            (court_length - self._goal_area_radius_in_centimeters, middle_court_width),  # 17: Right 6m arc, center
            (court_length - self._goal_area_radius_in_centimeters, goal_start + self._goal_width_in_centimeters),  # 18: Right 6m arc, top
            
            # Penalty spots (7m line)
            (self._penalty_spot_distance_in_centimeters, middle_court_width),  # 19: Left penalty spot
            (court_length - self._penalty_spot_distance_in_centimeters, middle_court_width),  # 20: Right penalty spot
            
            # 9m line key points (left side)
            (self._free_throw_line_distance_in_centimeters, goal_start),  # 21: Left 9m arc, bottom
            (self._free_throw_line_distance_in_centimeters, middle_court_width),  # 22: Left 9m arc, center
            (self._free_throw_line_distance_in_centimeters, goal_start + self._goal_width_in_centimeters),  # 23: Left 9m arc, top
            
            # 9m line key points (right side)
            (court_length - self._free_throw_line_distance_in_centimeters, goal_start),  # 24: Right 9m arc, bottom
            (court_length - self._free_throw_line_distance_in_centimeters, middle_court_width),  # 25: Right 9m arc, center
            (court_length - self._free_throw_line_distance_in_centimeters, goal_start + self._goal_width_in_centimeters),  # 26: Right 9m arc, top
            
            # Goalkeeper restraining line (4m line)
            (self._goalkeeper_restraining_line_in_centimeters, goal_start),  # 27: Left 4m line, bottom
            (self._goalkeeper_restraining_line_in_centimeters, goal_start + self._goal_width_in_centimeters),  # 28: Left 4m line, top
            (court_length - self._goalkeeper_restraining_line_in_centimeters, goal_start),  # 29: Right 4m line, bottom
            (court_length - self._goalkeeper_restraining_line_in_centimeters, goal_start + self._goal_width_in_centimeters),  # 30: Right 4m line, top
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
        (0, 1),  # Left baseline
        (0, 10),  # Left side, bottom half
        (10, 2),  # Right side, bottom half
        (2, 3),  # Right baseline
        (3, 11),  # Right side, top half
        (11, 1),  # Left side, top half
        
        # Center line
        (10, 11),
        
        # Goal lines (left side)
        (4, 5),  # Left goal line
        
        # Goal lines (right side)
        (7, 8),  # Right goal line
        
        # 6m goal area connections (left side)
        (13, 4),  # Bottom connection
        (15, 5),  # Top connection
        
        # 6m goal area connections (right side)
        (16, 7),  # Bottom connection
        (18, 8),  # Top connection
        
        # Goalkeeper restraining line (4m) (left side)
        (27, 28),
        
        # Goalkeeper restraining line (4m) (right side)
        (29, 30),
    ])

    labels: List[str] = field(default_factory=lambda: [
        "BL-Bottom", "BL-Top", "BR-Bottom", "BR-Top",  # 0-3: Corners
        "LG-Bottom", "LG-Top", "LG-Center",  # 4-6: Left goal
        "RG-Bottom", "RG-Top", "RG-Center",  # 7-9: Right goal
        "CL-Bottom", "CL-Top", "Center",  # 10-12: Center line
        "L6m-Bottom", "L6m-Center", "L6m-Top",  # 13-15: Left 6m line
        "R6m-Bottom", "R6m-Center", "R6m-Top",  # 16-18: Right 6m line
        "L-Penalty", "R-Penalty",  # 19-20: Penalty spots
        "L9m-Bottom", "L9m-Center", "L9m-Top",  # 21-23: Left 9m line
        "R9m-Bottom", "R9m-Center", "R9m-Top",  # 24-26: Right 9m line
        "L4m-Bottom", "L4m-Top", "R4m-Bottom", "R4m-Top",  # 27-30: 4m goalkeeper lines
    ])

    colors: List[str] = field(default_factory=lambda: [
        "#FF1493", "#FF1493", "#FF1493", "#FF1493",  # Corners: Pink
        "#00BFFF", "#00BFFF", "#00BFFF",  # Left goal: Blue
        "#00BFFF", "#00BFFF", "#00BFFF",  # Right goal: Blue
        "#A4F84B", "#A4F84B", "#A4F84B",  # Center: Green
        "#52F8C4", "#52F8C4", "#52F8C4",  # Left 6m: Teal
        "#52F8C4", "#52F8C4", "#52F8C4",  # Right 6m: Teal
        "#FF6B6B", "#FF6B6B",  # Penalty spots: Red
        "#FFA500", "#FFA500", "#FFA500",  # Left 9m: Orange
        "#FFA500", "#FFA500", "#FFA500",  # Right 9m: Orange
        "#9370DB", "#9370DB", "#9370DB", "#9370DB",  # 4m lines: Purple
    ])

    # Direct index getters
    @property
    def left_goal_area_indexes(self) -> List[int]:
        """Get vertex indexes defining the left goal area (6m line).
        
        Returns:
            `List[int]`: List of vertex indexes for left goal area.
        """
        return [4, 13, 14, 15, 5]

    @property
    def right_goal_area_indexes(self) -> List[int]:
        """Get vertex indexes defining the right goal area (6m line).
        
        Returns:
            `List[int]`: List of vertex indexes for right goal area.
        """
        return [7, 16, 17, 18, 8]

    @property
    def left_goal_index(self) -> int:
        """Get vertex index for the left goal center position.
        
        Returns:
            `int`: Vertex index for left goal center coordinates.
        """
        return 6

    @property
    def right_goal_index(self) -> int:
        """Get vertex index for the right goal center position.
        
        Returns:
            `int`: Vertex index for right goal center coordinates.
        """
        return 9

    @property
    def court_corner_indexes(self) -> List[int]:
        """Get vertex indexes for the four court corners.
        
        Returns:
            `List[int]`: List of vertex indexes for court corners in order:
                bottom-left, top-left, top-right, bottom-right.
        """
        return [0, 1, 3, 2]

    @property
    def left_penalty_spot_index(self) -> int:
        """Get vertex index for the left penalty spot (7m line).
        
        Returns:
            `int`: Vertex index for left penalty spot.
        """
        return 19

    @property
    def right_penalty_spot_index(self) -> int:
        """Get vertex index for the right penalty spot (7m line).
        
        Returns:
            `int`: Vertex index for right penalty spot.
        """
        return 20
