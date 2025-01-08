"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""

import time
from typing import Callable

import cv2
import mediapipe as mp
from mediapipe import Image
from mediapipe.framework.formats import landmark_pb2
from mediapipe.python.solutions import drawing_styles, hands
from mediapipe.python.solutions.drawing_utils import draw_landmarks
from mediapipe.python.solutions.hands import HandLandmark
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode,
)
from mediapipe.tasks.python.vision.gesture_recognizer import (
    GestureRecognizer,
    GestureRecognizerOptions,
    GestureRecognizerResult,
)
from pythonosc import udp_client

from point_handler.base import PointHandlerBase
from point_handler.note_generator import NoteGenerator
from point_handler.note_or_sequence import NoteOrSequence
from point_handler.synth_controller import SynthController

global_img, global_results = None, None

RIGHT_HAND_LABEL = 0
LEFT_HAND_lABEL = 1


def gesture_callback(result: GestureRecognizerResult, image: Image, _, handlers: tuple[PointHandlerBase]):
    global global_img, global_results
    annotated_image = image.numpy_view().copy()
    for landmarks in result.hand_landmarks:
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend(
            [
                landmark_pb2.NormalizedLandmark(
                    x=landmark.x, y=landmark.y, z=landmark.z
                )
                for landmark in landmarks
            ]
        )
        draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            hands.HAND_CONNECTIONS,
            drawing_styles.get_default_hand_landmarks_style(),
            drawing_styles.get_default_hand_connections_style(),
        )
    global_img = annotated_image
    global_results = result

    hand_indexes = {obj[0].index: i for i, obj in enumerate(result.handedness)}
    right_hand_index = hand_indexes.get(RIGHT_HAND_LABEL, None)
    left_hand_index = hand_indexes.get(LEFT_HAND_lABEL, None)
    if result.hand_landmarks:
        for handler in handlers:
            handler.handle(
                result.hand_landmarks[right_hand_index] if right_hand_index is not None else None,
                result.hand_landmarks[left_hand_index] if left_hand_index is not None else None,
                result.gestures[right_hand_index] if right_hand_index is not None else None,
                result.gestures[left_hand_index] if left_hand_index is not None else None,

            )
    # cv2.imshow("cenas", hand_landmarks_proto)
    # print(timestamp)


def load_model(handlers: tuple[PointHandlerBase, ...]):
    model_path = "./gesture_recognizer.task"
    func: Callable[[GestureRecognizerResult, Image, int], None] = lambda result, image, ts: gesture_callback(result, image, ts, handlers)
    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionTaskRunningMode.LIVE_STREAM,
        result_callback=func,
        num_hands=2,
    )
    return options


def run():
    client = udp_client.SimpleUDPClient("127.0.0.1", 4321)
    handlers = (
        NoteOrSequence(
            client,
            point1_index=HandLandmark.INDEX_FINGER_TIP,
            point2_index=HandLandmark.THUMB_TIP,
            note_endpoint="note",
            sequence_endpoint="sequence"
        ),
        NoteOrSequence(
            client,
            point1_index=HandLandmark.PINKY_TIP,
            point2_index=HandLandmark.RING_FINGER_DIP,
            note_endpoint="kick",
            sequence_endpoint="kick_sequence"
        ),
        SynthController(client)
    )
    options = load_model(handlers=handlers)
    webcam = cv2.VideoCapture(0)

    with GestureRecognizer.create_from_options(options) as recognizer:
        while webcam.isOpened():
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            ret, frame = webcam.read()

            if not ret:
                print("Failed to capture a frame")
                break

            current_timestamp_ms = int(time.time() * 1000)
            mp_image = Image(image_format=mp.ImageFormat.SRGB, data=cv2.flip(frame, 1))
            recognizer.recognize_async(mp_image, current_timestamp_ms)

            if global_img is not None:
                cv2.imshow("Hand Detection", global_img)


if __name__ == "__main__":
    run()
