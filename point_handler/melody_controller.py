import datetime
from mediapipe.python.solutions.hands import HandLandmark
from mediapipe.tasks.python.components.containers import Category
from pythonosc import udp_client
from .base import PointHandlerBase, hand

CAMERA_RESOLUTION = (1920, 1080)

class MelodyController(PointHandlerBase):
    def __init__(self, client: udp_client.SimpleUDPClient):
        super().__init__(client)
        self.last_gesture = False

    def handle(
            self,
            right_hand_points: hand | None,
            left_hand_points: hand | None,
            right_hand_gestures: list[Category] | None,
            left_hand_gestures: list[Category] | None,
    ) -> None:

        if left_hand_gestures is not None:
            is_pointing_up = any(g.category_name == "Pointing_Up" for g in left_hand_gestures)
        else:
            is_pointing_up = False
        if left_hand_points and is_pointing_up:
            self.client.send_message(
                "/melody_controls",
                [
                    1 - left_hand_points[HandLandmark.INDEX_FINGER_TIP].x,
                    1 - left_hand_points[HandLandmark.INDEX_FINGER_TIP].y,
                ],
            )
            if not self.last_gesture:
                self.client.send_message("/melody", 1)
                self.last_gesture = True
        else:
            if self.last_gesture:
                self.client.send_message("/melody", 0)
                self.last_gesture = False
