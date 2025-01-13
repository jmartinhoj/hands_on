import datetime

from mediapipe.tasks.python.components.containers import NormalizedLandmark, Category
from pythonosc import udp_client

from point_handler.base import PointHandlerBase, hand
from point_handler.utils import distance_between_points


class NoteOrSequence(PointHandlerBase):

    def __init__(self, client: udp_client.SimpleUDPClient, point1_index: int, point2_index: int, note_endpoint: str, sequence_endpoint: str, threshold: float):
        super().__init__(client)
        self.touching = False
        self.first_touch: datetime.datetime | None = None
        self.sequence_state = 0  # Track the current sequence state (0 or 1)
        self.sequence_sent = False  # Track if sequence message has been sent during the current touch
        self.point1_index = point1_index
        self.point2_index = point2_index
        self.note_endpoint = note_endpoint
        self.sequence_endpoint = sequence_endpoint
        self.threshold = threshold

    def _are_touching(self, p1: NormalizedLandmark, p2: NormalizedLandmark) -> bool:
        distance = distance_between_points((p1.x, p1.y), (p2.x, p2.y))
        return distance < self.threshold

    def handle(self, right_hand_points: hand | None, left_hand_points: hand | None, right_hand_gestures: list[Category] | None, left_hand_gestures: list[Category] | None,) -> None:
        if right_hand_points is None:
            return


        print(right_hand_gestures)
        if not any(g.category_name == "Open_Palm" for g in right_hand_gestures) and not any(g.category_name == "Unknown" for g in right_hand_gestures) and not any(g.category_name == "None" for g in right_hand_gestures):
            return

        index_tip = right_hand_points[self.point1_index]
        thumb_tip = right_hand_points[self.point2_index]

        if not self._are_touching(index_tip, thumb_tip):
            # Fingers are not touching
            if self.touching:
                self.touching = False
                self.first_touch = None  # Reset the touch timestamp
                self.sequence_sent = False  # Reset sequence sent status
                if self.sequence_state == 0:
                    # Only send a note-off message if the sequence is not playing
                    self.client.send_message(f"/{self.note_endpoint}", 0)
            return

        # Fingers are touching
        if not self.touching:
            # First contact detected
            self.touching = True
            self.first_touch = datetime.datetime.now(tz=datetime.timezone.utc)

            if self.sequence_state == 0:
                # Only send a note-on message if the sequence is not playing
                self.client.send_message(f"/{self.note_endpoint}", 1)
        else:
            # Check for sustained contact and toggle sequence
            if (
                not self.sequence_sent
                and self.first_touch is not None
                and (datetime.datetime.now(tz=datetime.timezone.utc) - self.first_touch).total_seconds() > 3
            ):
                # Toggle sequence state and send corresponding message
                self.sequence_state = 1 if self.sequence_state == 0 else 0
                self.client.send_message(f"/{self.sequence_endpoint}", self.sequence_state)
                self.sequence_sent = True  # Mark sequence as sent to avoid repeated sends