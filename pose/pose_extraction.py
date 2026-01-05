import cv2
import mediapipe as mp
import csv
import time

def extract_pose_to_csv(video_path: str, output_csv: str):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False)

    cap = cv2.VideoCapture(video_path)

    fieldnames = (
        ["timestamp"] +
        [f"lm_{i}_{axis}" for i in range(33) for axis in ["x", "y", "z"]]
    )

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)

            if not result.pose_landmarks:
                continue

            row = {"timestamp": timestamp}

            for i, lm in enumerate(result.pose_landmarks.landmark):
                row[f"lm_{i}_x"] = lm.x
                row[f"lm_{i}_y"] = lm.y
                row[f"lm_{i}_z"] = lm.z

            writer.writerow(row)

    cap.release()
    pose.close()

    print("Pose CSV erzeugt:", output_csv)