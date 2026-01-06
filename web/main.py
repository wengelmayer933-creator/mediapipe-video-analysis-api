from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
import uuid
import shutil
import json
from pathlib import Path

app = FastAPI(title="Mediapipe Video Analysis API")

# Pfade 
BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
SHARED_DIR = BASE_DIR / "shared"
JOBS_DIR = SHARED_DIR / "jobs"
RESULTS_DIR = SHARED_DIR / "results"
VIDEOS_DIR = SHARED_DIR / "videos"

# Ordner sicherstellen
UPLOADS_DIR.mkdir(exist_ok=True)
JOBS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {"status": "ok"}


# 1. Video hochladen & Job anlegen
@app.post("/analyze")
def analyze_video(file: UploadFile = File(...)):
    job_id = uuid.uuid4().hex[:8]

    input_path = UPLOADS_DIR / f"{job_id}.mp4"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job = {
        "job_id": job_id,
        "input_video": str(input_path)
    }

    with open(JOBS_DIR / f"{job_id}.json", "w") as f:
        json.dump(job, f)

    return {
        "job_id": job_id,
        "status": "processing"
    }


# 2. Status abfragen (UI polling)
@app.get("/status/{job_id}")
def get_status(job_id: str):
    result_file = RESULTS_DIR / f"{job_id}.json"

    if not result_file.exists():
        return {"status": "processing"}

    with open(result_file) as f:
        return json.load(f)


# 3. Ergebnisvideo ausliefern
@app.get("/result/{filename}")
def get_result_video(filename: str):
    video_path = VIDEOS_DIR / filename

    if not video_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "file not found"}
        )

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=filename
    )