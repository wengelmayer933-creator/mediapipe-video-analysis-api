from pathlib import Path
import pandas as pd
import numpy as np


GHOST_POSE_CSV = (
    "/Users/sebastianwengler/Desktop/"
    "Bewegungsdaten_Test/mediapipe_csv_preview/"
    "csv/ei_pose/ollie_reference.csv"
)

ghost_df = pd.read_csv(GHOST_POSE_CSV)
print("Ghost Pose geladen:", ghost_df.shape)
ghost_df.head()

GHOST_PHASE_ORDER = ["prep", "pop", "air", "land"]
SHOW_GHOST_IN_PHASES = {"prep", "pop", "air", "land"}


def generate_ghost_pose_reference(
    good_csv_dir: str,
    output_csv_path: str,
    phases=("prep", "pop", "air", "land")
):

    good_csv_dir = Path(good_csv_dir)
    output_csv_path = Path(output_csv_path)

    if not good_csv_dir.exists():
        raise FileNotFoundError(f"Input CSV-Ordner existiert nicht: {good_csv_dir}")

    good_csvs = sorted([
        p for p in good_csv_dir.iterdir()
        if p.name.startswith("ollie_gut") and p.suffix == ".csv"
    ])

    if not good_csvs:
        raise RuntimeError("Keine 'ollie_gut*.csv' Dateien gefunden")

    dfs = []
    for path in good_csvs:
        df = pd.read_csv(path)
        if "phase" in df.columns:
            dfs.append(df)

    if not dfs:
        raise RuntimeError("Keine gültigen CSVs mit 'phase' Spalte gefunden")

    print(f"{len(dfs)} gute Ollie-CSVs geladen")

    pose_cols = [
        c for c in dfs[0].columns
        if c.endswith("_x") or c.endswith("_y")
    ]

    reference_rows = []

    for phase in phases:
        phase_dfs = [
            df[df["phase"] == phase]
            for df in dfs
            if phase in df["phase"].values
        ]

        if not phase_dfs:
            continue

        combined = pd.concat(phase_dfs, ignore_index=True)

        mean_row = combined[pose_cols].mean()
        mean_row["phase"] = phase

        reference_rows.append(mean_row)

    if not reference_rows:
        raise RuntimeError("Keine Ghost-Pose-Daten erzeugt")

    ghost_df = pd.DataFrame(reference_rows)

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    ghost_df.to_csv(output_csv_path, index=False)

    print("Ghost Pose Referenz gespeichert:")
    print(output_csv_path)

    return ghost_df

import pandas as pd
from pathlib import Path


def load_ghost_pose(csv_path: str) -> pd.DataFrame:
    
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Ghost Pose CSV nicht gefunden: {csv_path}")

    df = pd.read_csv(csv_path)

    if "phase" not in df.columns:
        raise ValueError("Ghost Pose CSV muss eine 'phase'-Spalte enthalten")

    print("Ghost Pose geladen:", df.shape)
    return df
