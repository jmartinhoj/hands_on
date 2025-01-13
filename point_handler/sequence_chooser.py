import datetime
from mediapipe.python.solutions.hands import HandLandmark
from mediapipe.tasks.python.components.containers import Category
from pythonosc import udp_client
from .base import PointHandlerBase, hand


class SequenceChooser(PointHandlerBase):
    def __init__(self, client: udp_client.SimpleUDPClient):
        super().__init__(client)

    def handle(
            self,
            right_hand_points: hand | None,
            left_hand_points: hand | None,
            right_hand_gestures: list[Category] | None,
            left_hand_gestures: list[Category] | None,
    ) -> None:
        if right_hand_points:
            x_position = right_hand_points[HandLandmark.WRIST].x
            sequence = 0 if x_position < 0.1 else 1 if x_position < 0.2 else 2 if x_position < 0.3 else 3 if x_position < 0.4 else 4 if x_position < 0.5 else 5
            self.client.send_message(
                "/sequence_index",
                sequence
            )