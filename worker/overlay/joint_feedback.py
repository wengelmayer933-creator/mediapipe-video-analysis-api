import cv2
from feedback.angles import angle_3points
from rules import KNEE_ANGLE_RULES


def knee_state_phase(row, side, phase):
    hip = f"{side}_HIP"
    knee = f"{side}_KNEE"
    ankle = f"{side}_ANKLE"

    a = (row[f"{hip}_x"], row[f"{hip}_y"])
    b = (row[f"{knee}_x"], row[f"{knee}_y"])
    c = (row[f"{ankle}_x"], row[f"{ankle}_y"])

    angle = angle_3points(a, b, c)

    rules = KNEE_ANGLE_RULES.get(phase)
    if not rules:
        return "neutral"

    g_min, g_max = rules["green"]
    y_min, y_max = rules["yellow"]

    if g_min <= angle <= g_max:
        return "green"
    elif y_min <= angle <= y_max:
        return "yellow"
    else:
        return "red"

    
def draw_knee_feedback(frame, row, w, h, phase):
    states = {}

    colors = {
        "green": (0, 200, 0),
        "yellow": (0, 200, 200),
        "red": (0, 0, 255),
        "neutral": (160, 160, 160)
    }

    for side in ["LEFT", "RIGHT"]:
        state = knee_state_phase(row, side, phase)
        states[f"{side}_KNEE"] = state

        if state == "neutral":
            continue

        x = int(row[f"{side}_KNEE_x"] * w)
        y = int(row[f"{side}_KNEE_y"] * h)

        cv2.circle(frame, (x, y), 8, colors[state], -1)

    return states

def draw_hip_feedback(frame, row, w, h, phase):
    states = {}

    hip_x = (row["LEFT_HIP_x"] + row["RIGHT_HIP_x"]) / 2
    shoulder_x = (row["LEFT_SHOULDER_x"] + row["RIGHT_SHOULDER_x"]) / 2
    delta_x = abs(hip_x - shoulder_x)

    phase = str(phase).lower()

    if phase in ["prep", "pop"]:
        green_t, yellow_t = 0.025, 0.05
    else:
        green_t, yellow_t = 0.02, 0.04

    if delta_x < green_t:
        state = "green"
    elif delta_x < yellow_t:
        state = "yellow"
    else:
        state = "red"

    cx = int(hip_x * w)
    cy = int(((row["LEFT_HIP_y"] + row["RIGHT_HIP_y"]) / 2) * h)

    colors = {
        "green": (0, 200, 0),
        "yellow": (0, 200, 200),
        "red": (0, 0, 255)
    }

    cv2.circle(frame, (cx, cy), 10, colors[state], -1)

    states["HIP"] = state
    return states

def elbow_state(row, side, phase):
    s = f"{side}_SHOULDER"
    e = f"{side}_ELBOW"
    w = f"{side}_WRIST"

    a = (row[f"{s}_x"], row[f"{s}_y"])
    b = (row[f"{e}_x"], row[f"{e}_y"])
    c = (row[f"{w}_x"], row[f"{w}_y"])

    angle = angle_3points(a, b, c)
    phase = str(phase).lower()

    if phase == "air":
        if 120 < angle < 160:
            return "green"
        elif 100 < angle < 170:
            return "yellow"
        else:
            return "red"

    else:
        if angle > 140:
            return "green"
        elif angle > 120:
            return "yellow"
        else:
            return "red"
        
def draw_elbow_feedback(frame, row, w, h, phase):
    states = {}
    colors = {
        "green": (0, 200, 0),
        "yellow": (0, 200, 200),
        "red": (0, 0, 255)
    }

    for side in ["LEFT", "RIGHT"]:
        state = elbow_state(row, side, phase)
        states[f"{side}_ELBOW"] = state

        if state == "neutral":
            continue

        x = int(row[f"{side}_ELBOW_x"] * w)
        y = int(row[f"{side}_ELBOW_y"] * h)
        cv2.circle(frame, (x, y), 8, colors[state], -1)

    return states


def shoulder_state(row, side):
    other_side = "RIGHT" if side == "LEFT" else "LEFT"

    y1 = row[f"{side}_SHOULDER_y"]
    y2 = row[f"{other_side}_SHOULDER_y"]

    dy = abs(y1 - y2)

    if dy < 0.02:
        return "green"
    elif dy < 0.05:
        return "yellow"
    else:
        return "red"



def draw_shoulder_feedback(frame, row, w, h):
    states = {}
    colors = {
        "green": (0, 200, 0),
        "yellow": (0, 200, 200),
        "red": (0, 0, 255)
    }

    for side in ["LEFT", "RIGHT"]:
        state = shoulder_state(row, side)
        states[f"{side}_SHOULDER"] = state

        x = int(row[f"{side}_SHOULDER_x"] * w)
        y = int(row[f"{side}_SHOULDER_y"] * h)

        cv2.circle(frame, (x, y), 8, colors[state], -1)

    return states

def foot_state(row, side, phase):
    if str(phase).lower() == "air":
        return "neutral"

    hip = f"{side}_HIP"
    knee = f"{side}_KNEE"
    ankle = f"{side}_ANKLE"

    a = (row[f"{hip}_x"], row[f"{hip}_y"])
    b = (row[f"{knee}_x"], row[f"{knee}_y"])
    c = (row[f"{ankle}_x"], row[f"{ankle}_y"])

    angle = angle_3points(a, b, c)

    if angle < 140:
        return "green"
    elif angle < 160:
        return "yellow"
    else:
        return "red"

def draw_foot_feedback(frame, row, w, h, phase):
    states = {}
    colors = {
        "green": (0, 200, 0),
        "yellow": (0, 200, 200),
        "red": (0, 0, 255)
    }

    for side in ["LEFT", "RIGHT"]:
        state = foot_state(row, side, phase)
        states[f"{side}_FOOT"] = state

        if state == "neutral":
            continue

        x = int(row[f"{side}_ANKLE_x"] * w)
        y = int(row[f"{side}_ANKLE_y"] * h)
        cv2.circle(frame, (x, y), 8, colors[state], -1)

    return states