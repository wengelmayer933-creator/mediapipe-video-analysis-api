from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
import shutil
import os
import uuid
import pandas as pd

from pipeline import analyze_video_pipeline

app = FastAPI(title="Mediapipe Video Analysis API")


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_video(file: UploadFile = File(...)):
    # Eindeutige Job-ID
    job_id = uuid.uuid4().hex[:8]

    # Benötigte Ordner
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    # Upload speichern
    input_path = f"uploads/{job_id}_{file.filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Ghost CSV 
    ghost_csv_path = "ollie_ghost.csv"
    if not os.path.exists(ghost_csv_path):
        return JSONResponse(
            status_code=500,
            content={"error": "Ghost CSV not found"}
        )

    ghost_df = pd.read_csv(ghost_csv_path)

    # Analyse-Pipeline ausführen
    output_video_path = analyze_video_pipeline(
        input_video_path=input_path,
        ghost_df=ghost_df
    )

    # Nur Dateiname für URL verwenden
    output_filename = os.path.basename(output_video_path)

    return {
        "job_id": job_id,
        "result_url": f"/result/{output_filename}"
    }


@app.get("/result/{filename}")
def get_result_video(filename: str):
    file_path = os.path.join("temp", filename)

    if not os.path.exists(file_path):
        return JSONResponse(
            status_code=404,
            content={"error": "file not found"}
        )

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename
    )




