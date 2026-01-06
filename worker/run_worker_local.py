import pandas as pd
from pathlib import Path

from worker.pipeline import analyze_video_pipeline

if __name__ == "__main__":
    BASE = Path(__file__).resolve().parent.parent

    input_video = BASE / "uploads" / "test_input.mp4"
    ghost_csv = BASE / "shared" / "ollie_ghost.csv"

    if not input_video.exists():
        raise FileNotFoundError(f"Input video fehlt: {input_video}")

    ghost_df = pd.read_csv(ghost_csv)

    output = analyze_video_pipeline(
        input_video_path=str(input_video),
        ghost_df=ghost_df,
        work_dir=str(BASE / "temp")
    )

    print("Worker fertig")
    print("Output:", output)
