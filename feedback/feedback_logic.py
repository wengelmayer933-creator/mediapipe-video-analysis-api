import csv
import os
import cv2
import pandas as pd
import numpy as np
import math

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine, -1, 1)))


def extract_knee_angle(lm):
    left = calculate_angle(
        (lm[23].x, lm[23].y),
        (lm[25].x, lm[25].y),
        (lm[27].x, lm[27].y)
    )
    right = calculate_angle(
        (lm[24].x, lm[24].y),
        (lm[26].x, lm[26].y),
        (lm[28].x, lm[28].y)
    )
    return (left + right) / 2


def extract_hip_velocity(hips, ts):
    velocities = []
    for i in range(1, len(hips)):
        dy = hips[i-1] - hips[i]
        dt = (ts[i] - ts[i-1]) / 1000
        if dt > 0:
            velocities.append(dy / dt)
    return max(velocities) if velocities else 0


def extract_pop_timing(knees, ts):
    min_i = np.argmin(knees)
    max_i = np.argmax(knees[min_i:]) + min_i
    return (ts[max_i] - ts[min_i]) / 1000


def extract_ollie_features(frames):
    knees, hips, ts = [], [], []

    for f in frames:
        lm = f["landmarks"]
        knees.append(extract_knee_angle(lm))
        hips.append((lm[23].y + lm[24].y) / 2)
        ts.append(f["timestamp"])

    return {
        "knee_angle_min": float(np.min(knees)),
        "hip_velocity_max": float(extract_hip_velocity(hips, ts)),
        "pop_to_extend_time": float(extract_pop_timing(knees, ts))
    }

def extract_knee_angle(landmarks):
    
    def angle(a, b, c):
        ba = np.array([a.x - b.x, a.y - b.y])
        bc = np.array([c.x - b.x, c.y - b.y])
        cosang = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        return np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))

    left = angle(
        landmarks[23],  # hip
        landmarks[25],  # knee
        landmarks[27],  # ankle
    )

    right = angle(
        landmarks[24],
        landmarks[26],
        landmarks[28],
    )

    return (left + right) / 2




PHASE_FEEDBACK_RULES = {
    "prep": {
        "LEFT_KNEE": ["red", "yellow"],
        "RIGHT_KNEE": ["red", "yellow"],
        "HIP": ["red", "yellow"],
        "LEFT_ELBOW": ["yellow"],
        "RIGHT_ELBOW": ["yellow"],
    },
    "pop": {
        "LEFT_KNEE": ["red", "yellow"],
        "RIGHT_KNEE": ["red", "yellow"],
        "LEFT_ANKLE": ["red", "yellow"],
        "RIGHT_ANKLE": ["red", "yellow"],
        "HIP": ["red"],
    },
    "air": {
        "HIP": ["red", "yellow"],
        "LEFT_SHOULDER": ["yellow"],
        "RIGHT_SHOULDER": ["yellow"],
        "LEFT_ELBOW": ["yellow"],
        "RIGHT_ELBOW": ["yellow"],
    },
    "land": {
        "LEFT_KNEE": ["red", "yellow"],
        "RIGHT_KNEE": ["red", "yellow"],
        "HIP": ["red", "yellow"],
        "LEFT_ANKLE": ["red"],
        "RIGHT_ANKLE": ["red"],
    }
}


def is_feedback_allowed(joint, state, phase):
    phase = str(phase).lower()
    rules = PHASE_FEEDBACK_RULES.get(phase, {})
    allowed_states = rules.get(joint, [])
    return state in allowed_states


def is_person_visible(row, min_joints=5):
    required = [
        "LEFT_HIP", "RIGHT_HIP",
        "LEFT_SHOULDER", "RIGHT_SHOULDER",
        "LEFT_KNEE", "RIGHT_KNEE",
        "LEFT_ANKLE", "RIGHT_ANKLE"
    ]

    valid = 0
    for j in required:
        x = row.get(f"{j}_x", -1)
        y = row.get(f"{j}_y", -1)
        if 0.05 < x < 0.95 and 0.05 < y < 0.95:
            valid += 1

    return valid >= min_joints

def detect_ollie_phases(df):
    df = df.copy()

    # Glättung
    for c in ["LEFT_KNEE_y", "RIGHT_KNEE_y", "LEFT_ANKLE_y", "RIGHT_ANKLE_y"]:
        df[c + "_s"] = df[c].rolling(5, center=True).mean()

    df["lk_v"] = df["LEFT_KNEE_y_s"].diff()
    df["rk_v"] = df["RIGHT_KNEE_y_s"].diff()

    # 1 PREP
    prep_mask = (df["lk_v"] > 0.002) & (df["rk_v"] > 0.002)
    prep_idx = prep_mask[prep_mask].index
    prep_start = prep_idx[0] if len(prep_idx) else df.index[0]

    # 2 POP
    pop_candidates = df.loc[prep_start:, "lk_v"]
    pop_candidates = pop_candidates[pop_candidates < -0.006].index
    pop_idx = pop_candidates[0] if len(pop_candidates) else prep_start + 5
    pop_end = min(pop_idx + 2, df.index[-1])

    # 3 AIR
    la = df["LEFT_ANKLE_y_s"]
    ra = df["RIGHT_ANKLE_y_s"]

    air_mask = (
        (la < la.shift(1) - 0.002) &
        (ra < ra.shift(1) - 0.002)
    )

    air_candidates = air_mask[air_mask & (df.index > pop_end)].index
    air_start = air_candidates[0] if len(air_candidates) else pop_end + 1

    # 4 LAND
    ground_la = la.loc[prep_start:prep_start + 5].mean()
    ground_ra = ra.loc[prep_start:prep_start + 5].mean()

    land_mask = (
        (la > ground_la * 0.97) &
        (ra > ground_ra * 0.97)
    )

    land_candidates = land_mask[land_mask & (df.index > air_start)].index
    land_idx = land_candidates[0] if len(land_candidates) else df.index[-1]

    df["phase"] = "prep"
    df.loc[pop_idx:pop_end, "phase"] = "pop"
    df.loc[air_start:land_idx - 1, "phase"] = "air"
    df.loc[land_idx:, "phase"] = "land"

    return df
