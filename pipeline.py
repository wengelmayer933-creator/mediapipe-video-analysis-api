import os
import uuid
import shutil
import pandas as pd

from pose.pose_extraction import extract_pose_to_csv
from feedback.feedback_csv import generate_feedback_csv_from_pose
from overlay.video_overlay import live_overlay_video


def analyze_video_pipeline(
    input_video_path: str,
    ghost_df: pd.DataFrame,
    work_dir: str = "temp"
) -> str:
    

    # ---------- CHECK INPUT ----------
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input-Video existiert nicht:\n{input_video_path}")

    # ---------- SETUP ----------
    os.makedirs(work_dir, exist_ok=True)

    job_id = uuid.uuid4().hex[:8]

    video_path = os.path.join(work_dir, f"{job_id}_input.mp4")
    pose_csv = os.path.join(work_dir, f"{job_id}_pose.csv")
    feedback_csv = os.path.join(work_dir, f"{job_id}_feedback.csv")
    output_video = os.path.join(work_dir, f"{job_id}_analysis.mp4")

    shutil.copy(input_video_path, video_path)

    print("▶ Job:", job_id)
    print("▶ Input:", video_path)

    # ---------- 1. POSE ----------
    extract_pose_to_csv(
        video_path=video_path,
        output_csv=pose_csv
    )

    # ---------- 2. FEEDBACK ----------
    generate_feedback_csv_from_pose(
        pose_csv_path=pose_csv,
        out_path=feedback_csv
    )

    # ---------- 3. OVERLAY ----------
    live_overlay_video(
        video_path=video_path,
        feedback_csv=feedback_csv,
        ghost_df=ghost_df,
        output_path=output_video
    )

    print("Analyse fertig:", output_video)
    return output_video
