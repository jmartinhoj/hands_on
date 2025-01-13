import datetime
from mediapipe.python.solutions.hands import HandLandmark
from mediapipe.tasks.python.components.containers import Category
from pythonosc import udp_client
from .base import PointHandlerBase, hand


class ScaleController(PointHandlerBase):
    def __init__(self, client: udp_client.SimpleUDPClient):
        super().__init__(client)
        self.started_playing: datetime.datetime | None = None  # Time when fist was closed
        self.hold = False  # Whether we are in "hold" state
        self.last_gesture = "None"  # Tracks last gesture state

    def handle(
            self,
            right_hand_points: hand | None,
            left_hand_points: hand | None,
            right_hand_gestures: list[Category] | None,
            left_hand_gestures: list[Category] | None,
    ) -> None:
        if not right_hand_gestures:
            new_gesture = "None"
        elif any(g.category_name == "Thumb_Up" for g in right_hand_gestures):
            new_gesture = "thumbsup"
        elif any(g.category_name == "Thumb_Down" for g in right_hand_gestures):
            new_gesture = "thumbsdown"
        else:
            new_gesture = "None"
        print(new_gesture)

        if new_gesture != self.last_gesture:
            print("different")
            message_map = {
                "thumbsup": ("/scale", 1),
                "thumbsdown": ("/scale", -1),
            }
            if new_gesture in message_map:
                address, value = message_map[new_gesture]
                print(f"Sending message to {address} with value {value}")
                self.client.send_message(address, value)
            self.last_gesture = new_gesture
