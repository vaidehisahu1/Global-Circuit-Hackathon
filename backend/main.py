from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.ecg_analysis import process_ecg_data
import traceback

app = FastAPI(title="ECG Analysis API")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_ecg(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xml', '.aecg', '.bin', '.dat')):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    try:
        contents = await file.read()
        results = process_ecg_data(contents, file.filename)
        return results
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing ECG data: {str(e)}")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
