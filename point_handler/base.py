from abc import ABC, abstractmethod

from mediapipe.tasks.python.components.containers import NormalizedLandmark, Category
from pythonosc import udp_client

hand = list[NormalizedLandmark]


class PointHandlerBase(ABC):
    def __init__(self, client: udp_client.SimpleUDPClient):
        self.client = client

    @abstractmethod
    def handle(self, right_hand_points: hand | None, left_hand_points: hand | None,
               right_hand_gestures: list[Category] | None, left_hand_gestures: list[Category] | None) -> None:
        pass
