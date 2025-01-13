from mediapipe.tasks.python.components.containers import Category
from pythonosc import udp_client
from .base import PointHandlerBase, hand


class OctaveChooser(PointHandlerBase):
    def __init__(self, client: udp_client.SimpleUDPClient):
        super().__init__(client)
        self.last_gesture = None  # Tracks last gesture state (e.g., 'closed' or 'open')

    def handle(
            self,
            right_hand_points: hand | None,
            left_hand_points: hand | None,
            right_hand_gestures: list[Category] | None,
            left_hand_gestures: list[Category] | None,
    ) -> None:

        if right_hand_gestures:
            print("right hand gestures")
            if any(g.category_name == "Pointing_Up" for g in right_hand_gestures):
                if self.last_gesture != "Pointing_Up":
                    self.client.send_message("/octave", 3)
                    self.last_gesture = "Pointing_Up"
            elif any(g.category_name == "Victory" for g in right_hand_gestures):
                if self.last_gesture != "Victory":
                    self.client.send_message("/octave", 4)
                    self.last_gesture = "Victory"
            elif self.last_gesture != "None":
                self.client.send_message("/octave", 2)
                self.last_gesture = "None"

        elif self.last_gesture != "None":
            self.client.send_message("/octave", 2)
            self.last_gesture = "None"
