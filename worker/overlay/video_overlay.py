import cv2
import pandas as pd

# Ghost 
from draw_ghost import draw_ghost_pose, get_phase_ghost_row

# Skeleton 
from draw_skeleton import draw_colored_skeleton

# HUD 
from draw_hud import draw_feedback_hud, draw_phase_timeline

# Arrows 
from draw_arrows import draw_correction_arrow

# Joint Feedback Draws 
from joint_feedback import (
    draw_knee_feedback,
    draw_hip_feedback,
    draw_elbow_feedback,
    draw_shoulder_feedback,
    draw_foot_feedback,
)

# Feedback Logic 
from feedback.feedback_logic import (
    is_person_visible,
    is_feedback_allowed,
)


def live_overlay_video(
    video_path: str,
    feedback_csv: str,
    ghost_df: pd.DataFrame,
    output_path: str,
    show_ghost_in_phases=None,
):
    if show_ghost_in_phases is None:
        show_ghost_in_phases = {"prep", "pop", "air", "land"}

    df = pd.read_csv(feedback_csv)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Video konnte nicht geöffnet werden: {video_path}")

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    out = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h),
    )

    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        time_sec = frame_idx / fps
        pulse_phase = frame_idx / 6.0  # Ghost-Animation

        # nächste CSV-Zeile 
        row = df.iloc[(df["time_sec"] - time_sec).abs().argsort()[:1]].iloc[0]

        if not is_person_visible(row):
            out.write(frame)
            frame_idx += 1
            continue

        phase = str(row.get("phase", "")).lower()

        # GHOST POSE 
        if phase in show_ghost_in_phases:
            ghost_ref_row = get_phase_ghost_row(ghost_df, phase)
            if ghost_ref_row is not None:
                draw_ghost_pose(
                    frame,
                    ghost_ref_row,
                    w,
                    h,
                    alpha=0.45,
                    pulse_phase=pulse_phase,
                )

        # FEEDBACK 
        joint_states = {}
        joint_states.update(draw_knee_feedback(frame, row, w, h, phase))
        joint_states.update(draw_hip_feedback(frame, row, w, h, phase))
        joint_states.update(draw_elbow_feedback(frame, row, w, h, phase))
        joint_states.update(draw_shoulder_feedback(frame, row, w, h))
        joint_states.update(draw_foot_feedback(frame, row, w, h, phase))

        draw_colored_skeleton(frame, row, w, h, joint_states)
        draw_feedback_hud(frame, joint_states, phase)

        for joint, state in joint_states.items():
            if state in {"red", "yellow"} and is_feedback_allowed(joint, state, phase):
                draw_correction_arrow(frame, joint, row, w, h, state, phase)

        draw_phase_timeline(frame, phase)

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()

    return output_path

