import time
from pathlib import Path
import pandas as pd

from pipeline import analyze_video_pipeline

BASE = Path(__file__).resolve().parents[1]
UPLOADS = BASE / "uploads"
TEMP = BASE / "temp"
GHOST_CSV = BASE / "shared" / "ollie_ghost.csv"

print("Worker gestartet")
print("Uploads:", UPLOADS)
print("Temp:", TEMP)

UPLOADS.mkdir(exist_ok=True)
TEMP.mkdir(exist_ok=True)

ghost_df = pd.read_csv(GHOST_CSV)

processed = set()

while True:
    for video_path in UPLOADS.glob("*.mp4"):
        job_id = video_path.stem.split("_")[0]

        output_file = TEMP / f"{job_id}_analysis.mp4"

        if output_file.exists():
            continue

        if job_id in processed:
            continue

        print(f"Verarbeite Job {job_id}")

        try:
            analyze_video_pipeline(
                input_video_path=str(video_path),
                ghost_df=ghost_df,
                work_dir=str(TEMP),
            )
            print(f"✔ Job {job_id} fertig")
            processed.add(job_id)

        except Exception as e:
            print(f"Fehler bei Job {job_id}:", e)

    time.sleep(2)
