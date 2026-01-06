import os
import tempfile
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

from pipeline import analyze_video_pipeline


app = FastAPI(title="Video Worker")

# -------------------------
# Ghost CSV robust laden
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
GHOST_CSV = BASE_DIR / "shared" / "ollie_ghost.csv"

ghost_df = None

try:
    if not GHOST_CSV.exists():
        raise FileNotFoundError(f"Ghost CSV not found at {GHOST_CSV}")

    ghost_df = pd.read_csv(GHOST_CSV)
    print(f"Ghost CSV loaded: {GHOST_CSV}")

except Exception as e:
    # ⚠️ WICHTIG: Worker darf trotzdem starten!
    print("⚠️ Ghost CSV konnte nicht geladen werden:", e)


# -------------------------
# API
# -------------------------
@app.get("/")
def health():
    return {
        "status": "worker-ok",
        "ghost_loaded": ghost_df is not None,
        "ghost_path": str(GHOST_CSV),
    }


@app.post("/process")
async def process_video(file: UploadFile = File(...)):
    if ghost_df is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Ghost CSV not loaded"},
        )

    try:
        # Temp Input
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await file.read())
            input_path = tmp.name

        # Temp Output
        output_dir = Path(tempfile.mkdtemp())

        analyze_video_pipeline(
            input_video_path=input_path,
            ghost_df=ghost_df,
            work_dir=str(output_dir),
        )

        result_video = next(output_dir.glob("*_analysis.mp4"))

        return FileResponse(
            path=result_video,
            media_type="video/mp4",
            filename=result_video.name,
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


# -------------------------
# Entrypoint
# -------------------------
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
    )
