import cv2
from feedback.feedback_logic import is_feedback_allowed
from feedback_texts import JOINT_FEEDBACK_TEXT

def draw_feedback_hud(frame, joint_states, phase):
    h, w = frame.shape[:2]

   
    # HUD Box 
    box_x1, box_y1 = 20, 20
    box_x2, box_y2 = w - 20, 180

    overlay = frame.copy()
    cv2.rectangle(
        overlay,
        (box_x1, box_y1),
        (box_x2, box_y2),
        (0, 0, 0),
        -1
    )
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    
    # Ghost Pose Hinweis
    cv2.putText(
    frame,
    "Ghost Pose: reference from good ollies",
    (box_x1 + 20, box_y2 - 15),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    (0, 220, 255),
    2,
    cv2.LINE_AA
)

    # FEEDBACK sammeln 
    feedback_lines = []

    for joint, state in joint_states.items():
        if state == "green":
            continue
        if not is_feedback_allowed(joint, state, phase):
            continue

        text = (
            JOINT_FEEDBACK_TEXT
            .get(joint, {})
            .get(phase, {})
            .get(state)
        )

        if text:
            color = (0, 0, 255) if state == "red" else (0, 200, 200)
            feedback_lines.append((text, color))

    # TEXT 
    y = box_y1 + 30
    line_h = 26

    for text, color in feedback_lines[:5]:  # max 5 Zeilen
        cv2.putText(
            frame,
            f"- {text}",
            (box_x1 + 20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.95,
            color,
            2,
            cv2.LINE_AA
        )
        y += line_h

    # LEGENDE 
 
    lx = box_x2 - 260
    ly = box_y1 + 30

    legend = [
        ("GOOD", (0, 200, 0)),
        ("OK", (0, 200, 200)),
        ("CORRECT", (0, 0, 255))
    ]

    for label, color in legend:
        cv2.rectangle(frame, (lx, ly - 12), (lx + 20, ly + 8), color, -1)
        cv2.putText(
            frame,
            label,
            (lx + 30, ly + 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        ly += 26

def draw_phase_timeline(frame, phase):
    phases = ["prep", "pop", "air", "land"]
    labels = {
        "prep": "PREP",
        "pop": "POP",
        "air": "AIR",
        "land": "LAND"
    }

    h, w = frame.shape[:2]

    bar_w = 130   
    bar_h = 28
    gap = 16

    total_w = len(phases) * bar_w + (len(phases) - 1) * gap
    start_x = (w - total_w) // 2
    y = h - 70

    for i, p in enumerate(phases):
        x = start_x + i * (bar_w + gap)

        color = (0, 200, 200) if p == phase else (60, 60, 60)

        cv2.rectangle(frame, (x, y), (x + bar_w, y + bar_h), color, -1)

        cv2.putText(
            frame,
            labels[p],
            (x + 35, y + 20),
            cv2.FONT_HERSHEY_DUPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )