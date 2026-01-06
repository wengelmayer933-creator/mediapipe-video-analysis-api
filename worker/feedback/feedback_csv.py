import csv
import os
import cv2
import pandas as pd
import numpy as np

from feedback.feedback_logic import (
    extract_knee_angle,
    detect_ollie_phases
)

def load_frames_from_csv(csv_path):
    import pandas as pd

    df = pd.read_csv(csv_path)

    frames = []

    for _, row in df.iterrows():
        landmarks = []

        for i in range(33):
            lm = type("LM", (), {})()
            lm.x = row[f"lm_{i}_x"]
            lm.y = row[f"lm_{i}_y"]
            lm.z = row.get(f"lm_{i}_z", 0.0)
            landmarks.append(lm)

        frames.append({
            "timestamp": row["timestamp"],
            "landmarks": landmarks
        })

    return frames

def generate_feedback_csv_from_pose(pose_csv_path, out_path):
    import pandas as pd

    df_pose = pd.read_csv(pose_csv_path)
    rows = []

    for _, row in df_pose.iterrows():
        lm = []

        for i in range(33):
            lm.append(
                type("LM", (), {
                    "x": row[f"lm_{i}_x"],
                    "y": row[f"lm_{i}_y"],
                    "z": row.get(f"lm_{i}_z", 0.0)
                })
            )

        timestamp = row["timestamp"]
        time_sec = timestamp / 1000.0

        knee_angle = extract_knee_angle(lm)
        hip_y = (lm[23].y + lm[24].y) / 2

        rows.append({
            "timestamp": timestamp,
            "time_sec": time_sec,
            "knee_angle": knee_angle,
            "hip_y": hip_y,

            # Beine
            "LEFT_HIP_x": lm[23].x,   "LEFT_HIP_y": lm[23].y,
            "LEFT_KNEE_x": lm[25].x,  "LEFT_KNEE_y": lm[25].y,
            "LEFT_ANKLE_x": lm[27].x, "LEFT_ANKLE_y": lm[27].y,

            "RIGHT_HIP_x": lm[24].x,   "RIGHT_HIP_y": lm[24].y,
            "RIGHT_KNEE_x": lm[26].x,  "RIGHT_KNEE_y": lm[26].y,
            "RIGHT_ANKLE_x": lm[28].x, "RIGHT_ANKLE_y": lm[28].y,

            # Oberkörper
            "LEFT_SHOULDER_x": lm[11].x,  "LEFT_SHOULDER_y": lm[11].y,
            "RIGHT_SHOULDER_x": lm[12].x, "RIGHT_SHOULDER_y": lm[12].y,

            "LEFT_ELBOW_x": lm[13].x,  "LEFT_ELBOW_y": lm[13].y,
            "RIGHT_ELBOW_x": lm[14].x, "RIGHT_ELBOW_y": lm[14].y,

            "LEFT_WRIST_x": lm[15].x,  "LEFT_WRIST_y": lm[15].y,
            "RIGHT_WRIST_x": lm[16].x, "RIGHT_WRIST_y": lm[16].y,
        })

    df_feedback = pd.DataFrame(rows)

    if "phase" not in df_feedback.columns:
        df_feedback = detect_ollie_phases(df_feedback)

    df_feedback.to_csv(out_path, index=False)

    print("Feedback CSV erzeugt:", out_path)
    return out_path
