import datetime
from mediapipe.python.solutions.hands import HandLandmark
from mediapipe.tasks.python.components.containers import Category
from pythonosc import udp_client
from .base import PointHandlerBase, hand

CAMERA_RESOLUTION = (1920, 1080)

class SynthController(PointHandlerBase):
    def __init__(self, client: udp_client.SimpleUDPClient):
        super().__init__(client)
        self.started_playing: datetime.datetime | None = None  # Time when fist was closed
        self.hold = False  # Whether we are in "hold" state
        self.last_gesture = None  # Tracks last gesture state (e.g., 'closed' or 'open')

    def handle(
            self,
            right_hand_points: hand | None,
            left_hand_points: hand | None,
            right_hand_gestures: list[Category] | None,
            left_hand_gestures: list[Category] | None,
    ) -> None:
        print("hold", self.hold)
        if left_hand_points and not self.hold:
            self.client.send_message(
                "/synth_controls",
                [
                    1 - left_hand_points[HandLandmark.WRIST].x,
                    1 - left_hand_points[HandLandmark.WRIST].y,
                ],
            )

        if left_hand_gestures:
            is_fist_closed = any(g.category_name == "Closed_Fist" for g in left_hand_gestures)

            if is_fist_closed:
                if self.last_gesture != "closed":
                    print("Fist closed. Sending 1.")
                    self.hold = False  # Reset hold
                    self.started_playing = datetime.datetime.now()  # Start timer
                    if not self.hold:
                        self.client.send_message("/synth", 1)
                elif self.started_playing and (datetime.datetime.now() - self.started_playing).seconds >= 5:
                    print("Hold triggered.")
                    self.hold = True  # Enter hold state
            else:
                if self.last_gesture == "closed":
                    if not self.hold:
                        print("Fist opened. Sending 0.")
                        self.client.send_message("/synth", 0)
                    else:
                        print("Fist opened after hold. No 0 sent.")
                    # self.hold = False  # Reset hold
                self.started_playing = None  # Reset time when opened

            self.last_gesture = "closed" if is_fist_closed else "open"