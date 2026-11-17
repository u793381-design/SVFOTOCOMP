import os
import shutil
import uuid
import subprocess
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

APP_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = APP_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_BYTES = 16 * 1024 * 1024 * 1024
CHUNK_SIZE = 1024 * 1024
ALLOWED_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi", ".webm"}

app = FastAPI(title="SVFOTOCOMP API", version="0.1.0")

# Development convenience only. Restrict this to your Mini App domain before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "SVFOTOCOMP API", "status": "running", "version": "0.1.0"}

@app.get("/health")
def health():
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    return {
        "ok": True,
        "ffmpeg_available": bool(ffmpeg),
        "ffprobe_available": bool(ffprobe),
    }

@app.post("/api/upload")
async def upload_match(
    video: UploadFile = File(...),
    player_name: str = Form(...),
    shirt_number: int = Form(...)
):
    original_name = Path(video.filename or "match-video").name
    suffix = Path(original_name).suffix.lower()

    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, "Desteklenmeyen video uzantısı.")
    if not player_name.strip():
        raise HTTPException(400, "Oyuncu adı boş olamaz.")
    if shirt_number < 0 or shirt_number > 999:
        raise HTTPException(400, "Forma numarası 0-999 arasında olmalı.")

    file_id = uuid.uuid4().hex
    destination = UPLOAD_DIR / f"{file_id}{suffix}"
    total = 0

    try:
        with destination.open("wb") as out:
            while True:
                chunk = await video.read(CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_BYTES:
                    raise HTTPException(413, "Video 16 GB sınırını aşıyor.")
                out.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await video.close()

    if total == 0:
        destination.unlink(missing_ok=True)
        raise HTTPException(400, "Boş dosya yüklenemez.")

    metadata = {"duration_seconds": None, "video_codec": None}
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        try:
            result = subprocess.run(
                [
                    ffprobe, "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=codec_name:format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(destination),
                ],
                capture_output=True, text=True, timeout=30, check=True
            )
            lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            if lines:
                # ffprobe usually returns codec then duration for these selected fields.
                for line in lines:
                    try:
                        metadata["duration_seconds"] = float(line)
                    except ValueError:
                        metadata["video_codec"] = line
        except Exception:
            pass

    return {
        "ok": True,
        "file_id": file_id,
        "filename": original_name,
        "size_bytes": total,
        "player_name": player_name.strip(),
        "shirt_number": shirt_number,
        "metadata": metadata,
        "message": "Video sunucuya alındı. Otomatik oyuncu tespiti henüz eklenmedi."
    }
