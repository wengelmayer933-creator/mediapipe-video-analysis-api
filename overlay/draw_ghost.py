import numpy as np
import cv2
import numpy as np



def get_phase_ghost_row(ghost_df, phase):
    phase = str(phase).lower()

    rows = ghost_df[ghost_df["phase"] == phase]
    if len(rows) == 0:
        return None

    return rows.iloc[0]

def interpolate_ghost_pose(row_a, row_b, t):
    
    interp = {}

    for c in row_a.index:
        if c.endswith("_x") or c.endswith("_y"):
            interp[c] = (1 - t) * row_a[c] + t * row_b[c]

    return pd.Series(interp)

def draw_ghost_pose(frame, ref_row, w, h, alpha=0.45, pulse_phase=0.0):
  
    ghost = frame.copy()

    ghost_color = (0, 220, 255)  # Cyan
    thickness = 4

    y_offset = int(3 * np.sin(pulse_phase))

    connections = [
        ("LEFT_SHOULDER", "RIGHT_SHOULDER"),
        ("LEFT_SHOULDER", "LEFT_ELBOW"),
        ("LEFT_ELBOW", "LEFT_WRIST"),
        ("RIGHT_SHOULDER", "RIGHT_ELBOW"),
        ("RIGHT_ELBOW", "RIGHT_WRIST"),
        ("LEFT_HIP", "RIGHT_HIP"),
        ("LEFT_SHOULDER", "LEFT_HIP"),
        ("RIGHT_SHOULDER", "RIGHT_HIP"),
        ("LEFT_HIP", "LEFT_KNEE"),
        ("LEFT_KNEE", "LEFT_ANKLE"),
        ("RIGHT_HIP", "RIGHT_KNEE"),
        ("RIGHT_KNEE", "RIGHT_ANKLE"),
    ]

    for j1, j2 in connections:
        if f"{j1}_x" not in ref_row or f"{j2}_x" not in ref_row:
            continue

        x1 = int(ref_row[f"{j1}_x"] * w)
        y1 = int(ref_row[f"{j1}_y"] * h) + y_offset
        x2 = int(ref_row[f"{j2}_x"] * w)
        y2 = int(ref_row[f"{j2}_y"] * h) + y_offset

        cv2.line(ghost, (x1, y1), (x2, y2), ghost_color, thickness)

    pulse_alpha = alpha + 0.1 * np.sin(pulse_phase)

    cv2.addWeighted(ghost, pulse_alpha, frame, 1 - pulse_alpha, 0, frame)

