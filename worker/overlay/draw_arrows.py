import cv2
from feedback.feedback_logic import is_feedback_allowed
from overlay.rules import JOINT_ARROW_RULES

def draw_correction_arrow(frame, joint, row, w, h, state, phase):
    if not is_feedback_allowed(joint, state, phase):
        return

    rule = JOINT_ARROW_RULES.get(joint)
    if not rule:
        return

    x = int(row[f"{joint}_x"] * w)
    y = int(row[f"{joint}_y"] * h)

    end = (x + rule["dx"], y + rule["dy"])

    cv2.arrowedLine(
        frame,
        (x, y),
        end,
        (0, 0, 255),
        3,
        tipLength=0.25,
        line_type=cv2.LINE_AA
    )