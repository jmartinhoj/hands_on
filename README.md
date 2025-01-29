# Gesture-Controlled Music System

This project is an interactive audio system that leverages **PureData (PlugData)** for audio synthesis, **Python** for gesture-based control using **computer vision**, and **Reaper** for MIDI and VST instrument management. The system enables real-time performance and automatic composition based on hand gestures.

---

## Project Overview

- **Python Script (`main.py`)**: Handles gesture detection using computer vision.
- **PureData (PlugData)**: Receives OSC data from the Python script to generate MIDI signals for sequences, harmonies, and melodies.
- **Reaper Project (`instruments.rpp`)**: Contains the instrument configuration, including the **Korg Berlin Prototype Phase 8** VST for advanced sound synthesis.

---

## Gesture Controls

### Left Hand Gestures:
- **Index Tip on Thumb Tip**:
  - **Action**: Starts playing a note from the sequence \( x[k+1] = A + (x[k] + B) \mod C \).
  - **Hold Gesture**: Continuously plays the sequence.
  - **Output**: Sends MIDI note to **Reaper**.

- **Thumb Up/Down**:
  - **Action**: Changes the musical scale.
  - **Options**: `C Major`, `C Doric`, `G Doric`.

- **Pointing Up**:
  - **Action**: Increases the MIDI note by 1 octave.

- **Victory Sign (V Sign)**:
  - **Action**: Increases the MIDI note by 2 octaves.

- **X Position of the Left Hand**:
  - **Action**: Varies the `A`, `B`, and `C` parameters of the sequence.

### Right Hand Gestures:
- **Closed Fist**:
  - **Action**: Plays a harmony using oscillators in PlugData (the volume of the harmony varies according to the X position of the hand).
  - **Hold Gesture**: Sustains the harmony.

- **Pointing Up**:
  - **Action**: Plays a melody.
  - **Note Frequency**: Based on the X-axis position of the right hand.

---

## Installation

1. Enter the folder
```bash
cd hands_on
```

2. **Install Dependencies**: Install the required dependencies from requirements.txt:
```bash
pip install -r requirements.txt
```

3. Additional Software
	- PlugData: Download and install PlugData.
	- Reaper: Download and install Reaper DAW.
	- Korg Berlin Prototype Phase 8 VST: Ensure that the VST is installed and configured in Reaper.

## Usage
1.	Run the Python Gesture Detection Script:
```bash
python main.py
```
2.	Open PlugData Patch:
	- Open the PureData (PlugData) script to handle OSC messages and audio processing.
3.	Load Reaper Project:
	- Open instruments.rpp in Reaper.
4.	Perform Gestures:
	- Move your hands in front of the camera as described in the gesture controls.
	- The audio and MIDI notes will be triggered and modified in real time.

