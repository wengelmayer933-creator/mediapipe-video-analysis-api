import cv2


SKELETON_EDGES = [
    # Beine
    ("LEFT_HIP", "LEFT_KNEE"),
    ("LEFT_KNEE", "LEFT_ANKLE"),
    ("RIGHT_HIP", "RIGHT_KNEE"),
    ("RIGHT_KNEE", "RIGHT_ANKLE"),

    # Hüfte / Oberkörper
    ("LEFT_HIP", "RIGHT_HIP"),
    ("LEFT_SHOULDER", "RIGHT_SHOULDER"),
    ("LEFT_HIP", "LEFT_SHOULDER"),
    ("RIGHT_HIP", "RIGHT_SHOULDER"),

    # Arme
    ("LEFT_SHOULDER", "LEFT_ELBOW"),
    ("LEFT_ELBOW", "LEFT_WRIST"),
    ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
    ("RIGHT_ELBOW", "RIGHT_WRIST"),
]

def draw_colored_skeleton(frame, row, w, h, joint_states):
    colors = {
        "green": (0, 200, 0),
        "yellow": (0, 200, 200),
        "red": (0, 0, 255),
        "neutral": (180, 180, 180)
    }

    for a, b in SKELETON_EDGES:
        if f"{a}_x" not in row or f"{b}_x" not in row:
            continue

        ax, ay = int(row[f"{a}_x"] * w), int(row[f"{a}_y"] * h)
        bx, by = int(row[f"{b}_x"] * w), int(row[f"{b}_y"] * h)

        # Farbe bestimmen
        state = joint_states.get(a) or joint_states.get(b)
        color = colors.get(state, colors["neutral"])

        cv2.line(frame, (ax, ay), (bx, by), color, 3)