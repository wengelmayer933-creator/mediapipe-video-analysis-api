from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import pandas as pd

from pipeline import analyze_video_pipeline

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/analyze")
def analyze_video(file: UploadFile = File(...)):
    job_id = uuid.uuid4().hex[:8]

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    input_path = f"uploads/{job_id}_{file.filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ghost_df = pd.read_csv(
        "csv/ei_pose/ollie_gut_Ollie37_feedback.csv"
    )

    output_video = analyze_video_pipeline(
        input_video_path=input_path,
        ghost_df=ghost_df
    )

    return JSONResponse({
        "job_id": job_id,
        "result_video": output_video
    })
