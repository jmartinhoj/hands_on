import datetime

from mediapipe.python.solutions.hands import HandLandmark
from mediapipe.tasks.python.components.containers import NormalizedLandmark
from pythonosc import udp_client

from .utils import distance_between_points
from .base import PointHandlerBase, hand


class NoteGenerator(PointHandlerBase):
    def __init__(self, client: udp_client.SimpleUDPClient):
        super().__init__(client)
        self.touching = False
        self.first_touch: datetime.datetime | None = None
        self.sequence_state = 0  # Track the current sequence state (0 or 1)
        self.sequence_sent = False  # Track if sequence message has been sent during the current touch

    @staticmethod
    def _are_touching(p1: NormalizedLandmark, p2: NormalizedLandmark) -> bool:
        distance = distance_between_points((p1.x, p1.y), (p2.x, p2.y))
        return distance < 0.1

    def handle(self, right_hand_points: hand | None, left_hand_points: hand | None, *_) -> None:
        if right_hand_points is None:
            return

        index_tip = right_hand_points[HandLandmark.INDEX_FINGER_TIP]
        thumb_tip = right_hand_points[HandLandmark.THUMB_TIP]

        if not self._are_touching(index_tip, thumb_tip):
            # Fingers are not touching
            if self.touching:
                self.touching = False
                self.first_touch = None  # Reset the touch timestamp
                self.sequence_sent = False  # Reset sequence sent status
                self.client.send_message("/note", 0)
            return

        # Fingers are touching
        if not self.touching:
            # First contact detected
            self.touching = True
            self.first_touch = datetime.datetime.now(tz=datetime.timezone.utc)
            self.client.send_message("/note", 1)
        else:
            # Check for sustained contact and toggle sequence
            if (
                not self.sequence_sent
                and self.first_touch is not None
                and (datetime.datetime.now(tz=datetime.timezone.utc) - self.first_touch).total_seconds() > 3
            ):
                # Toggle sequence state and send corresponding message
                self.sequence_state = 1 if self.sequence_state == 0 else 0
                self.client.send_message("/sequence", self.sequence_state)
                self.sequence_sent = True  # Mark sequence as sent to avoid repeated sends