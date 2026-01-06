from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import uuid
import requests

app = FastAPI(title="Video Analysis API")

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# 👉 HIER DIE WORKER-URL EINTRAGEN
WORKER_URL = "https://skate-worker.onrender.com/process"


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_video(file: UploadFile = File(...)):
    job_id = uuid.uuid4().hex[:8]

    try:
        response = requests.post(
            WORKER_URL,
            files={
                "file": (
                    file.filename,
                    file.file,
                    file.content_type,
                )
            },
            timeout=900,  # 15 Minuten
        )

    except requests.RequestException as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )

    if response.status_code != 200:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Worker failed",
                "worker_status": response.status_code,
                "worker_response": response.text,
         },
    )


    output_path = RESULTS_DIR / f"{job_id}.mp4"

    with open(output_path, "wb") as f:
        f.write(response.content)

    return {
        "job_id": job_id,
        "status": "done",
        "result_url": f"/result/{output_path.name}",
    }


@app.get("/result/{filename}")
def get_result(filename: str):
    file_path = RESULTS_DIR / filename

    if not file_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": "file not found"},
        )

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=filename,
    )
