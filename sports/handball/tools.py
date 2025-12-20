from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Literal, TypedDict


BALL_IN_GOAL_MIN_CONSECUTIVE_FRAMES = 2
JUMP_SHOT_MIN_CONSECUTIVE_FRAMES = 3
BREAKTHROUGH_MIN_CONSECUTIVE_FRAMES = 3


class ShotType(Enum):
    NONE = "NONE"
    JUMP = "JUMP"
    PENALTY = "PENALTY"
    BREAKTHROUGH = "BREAKTHROUGH"


class ShotEvent(Enum):
    START = "START"
    MADE = "MADE"
    MISSED = "MISSED"


class ShotEventRecord(TypedDict):
    event: Literal["START", "MADE", "MISSED"]
    frame: int
    type: Literal["NONE", "JUMP", "PENALTY", "BREAKTHROUGH"]


@dataclass
class ShotEventTracker:
    """Track shot events in handball games.
    
    Monitors different types of handball shots (jump shots, penalties, breakthroughs)
    and detects when they start, are made, or are missed based on consecutive frame detection.
    
    Args:
        reset_time_frames: Maximum frames to wait for shot completion before marking as missed
        minimum_frames_between_starts: Minimum frames between consecutive shot starts
        cooldown_frames_after_made: Cooldown period after a successful goal before allowing new shot detection
    """
    reset_time_frames: int
    minimum_frames_between_starts: int
    cooldown_frames_after_made: int

    shot_in_progress: bool = False
    shot_type: ShotType = ShotType.NONE
    shot_start_frame: Optional[int] = None
    shot_deadline_frame: Optional[int] = None
    frames_since_start: int = 0

    consecutive_jump_shot_frames: int = 0
    consecutive_penalty_frames: int = 0
    consecutive_breakthrough_frames: int = 0
    consecutive_ball_in_goal_frames: int = 0

    last_made_frame: Optional[int] = None

    def update(
        self,
        frame_index: int,
        has_jump_shot: bool,
        has_penalty: bool,
        has_breakthrough: bool,
        has_ball_in_goal: bool,
    ) -> List[ShotEventRecord]:
        """Update tracker state and detect shot events.
        
        Args:
            frame_index: Current frame number
            has_jump_shot: Whether a jump shot is detected in this frame
            has_penalty: Whether a penalty shot (7m) is detected in this frame
            has_breakthrough: Whether a breakthrough is detected in this frame
            has_ball_in_goal: Whether the ball is detected in the goal in this frame
        
        Returns:
            List[ShotEventRecord]: List of detected shot events (START, MADE, MISSED)
        """
        events: List[ShotEventRecord] = []

        self.consecutive_jump_shot_frames = self._updated_consecutive_frames(
            self.consecutive_jump_shot_frames, has_jump_shot
        )
        self.consecutive_penalty_frames = self._updated_consecutive_frames(
            self.consecutive_penalty_frames, has_penalty
        )
        self.consecutive_breakthrough_frames = self._updated_consecutive_frames(
            self.consecutive_breakthrough_frames, has_breakthrough
        )
        self.consecutive_ball_in_goal_frames = self._updated_consecutive_frames(
            self.consecutive_ball_in_goal_frames, has_ball_in_goal
        )

        reached_jump_shot_threshold = (
            self.consecutive_jump_shot_frames == JUMP_SHOT_MIN_CONSECUTIVE_FRAMES
        )
        reached_penalty_threshold = (
            self.consecutive_penalty_frames == JUMP_SHOT_MIN_CONSECUTIVE_FRAMES
        )
        reached_breakthrough_threshold = (
            self.consecutive_breakthrough_frames == BREAKTHROUGH_MIN_CONSECUTIVE_FRAMES
        )
        should_start_shot = (
            reached_jump_shot_threshold 
            or reached_penalty_threshold 
            or reached_breakthrough_threshold
        )

        if should_start_shot and self._within_post_made_cooldown(frame_index):
            should_start_shot = False

        if should_start_shot:
            if self.shot_in_progress:
                if self.frames_since_start >= self.minimum_frames_between_starts:
                    events.append(self._missed_event(frame_index))
                    self._reset_shot_state()
                else:
                    should_start_shot = False

            if should_start_shot:
                if reached_jump_shot_threshold:
                    shot_type = ShotType.JUMP
                elif reached_penalty_threshold:
                    shot_type = ShotType.PENALTY
                else:
                    shot_type = ShotType.BREAKTHROUGH
                
                self._start_new_shot(shot_type, frame_index)
                events.append(self._start_event(frame_index))

        if self.shot_in_progress:
            self.frames_since_start += 1

            if self._has_confirmed_make():
                events.append(self._made_event(frame_index))
                self.last_made_frame = frame_index
                self._reset_shot_state()
                return events

            if self._deadline_reached(frame_index):
                events.append(self._missed_event(frame_index))
                self._reset_shot_state()
                return events

        return events

    @staticmethod
    def _updated_consecutive_frames(current_count: int, detected: bool) -> int:
        return current_count + 1 if detected else 0

    def _start_new_shot(self, shot_type: ShotType, frame_index: int) -> None:
        self.shot_in_progress = True
        self.shot_type = shot_type
        self.shot_start_frame = frame_index
        self.shot_deadline_frame = frame_index + self.reset_time_frames
        self.frames_since_start = 0
        self.consecutive_ball_in_goal_frames = 0

    def _has_confirmed_make(self) -> bool:
        return (
            self.consecutive_ball_in_goal_frames
            >= BALL_IN_GOAL_MIN_CONSECUTIVE_FRAMES
        )

    def _deadline_reached(self, frame_index: int) -> bool:
        return (
            self.shot_deadline_frame is not None
            and frame_index >= self.shot_deadline_frame
        )

    def _within_post_made_cooldown(self, frame_index: int) -> bool:
        if self.last_made_frame is None:
            return False
        return (frame_index - self.last_made_frame) < self.cooldown_frames_after_made

    def _start_event(self, frame_index: int) -> ShotEventRecord:
        return {"event": ShotEvent.START.value, "frame": frame_index, "type": self.shot_type.value}

    def _made_event(self, frame_index: int) -> ShotEventRecord:
        return {"event": ShotEvent.MADE.value, "frame": frame_index, "type": self.shot_type.value}

    def _missed_event(self, frame_index: int) -> ShotEventRecord:
        return {"event": ShotEvent.MISSED.value, "frame": frame_index, "type": self.shot_type.value}

    def _reset_consecutive_counters(self) -> None:
        self.consecutive_jump_shot_frames = 0
        self.consecutive_penalty_frames = 0
        self.consecutive_breakthrough_frames = 0
        self.consecutive_ball_in_goal_frames = 0

    def _reset_shot_state(self) -> None:
        self.shot_in_progress = False
        self.shot_type = ShotType.NONE
        self.shot_start_frame = None
        self.shot_deadline_frame = None
        self.frames_since_start = 0
        self._reset_consecutive_counters()
