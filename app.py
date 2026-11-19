import os
import sys
import time
import uuid
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

# Set working directory to project root
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from scripts.pipeline import run_job
from scripts.gdrive_upload import upload_file_to_drive

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("UniversalClipperApp")

app = FastAPI(
    title="Universal AI Video Clipper API",
    description="Autonomous Pipeline to clip YouTube streams/VODs into 9:16 viral Shorts with AI face-tracking & karaoke captions.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job state store
jobs: Dict[str, Dict[str, Any]] = {}

FINAL_DIR = BASE_DIR / "final_clips"
FINAL_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = BASE_DIR / "temp_work"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

class ClipRequest(BaseModel):
    url: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    output_filename: Optional[str] = None
    upload_to_gdrive: bool = False
    gdrive_folder_id: Optional[str] = None
    force_pillarbox: bool = False

def auto_delete_file(file_path: Path):
    """Deletes a rendered file from server disk to keep storage usage at 0 MB."""
    try:
        if file_path.exists():
            time.sleep(2)  # Give the HTTP response stream 2s buffer to finish transmission
            file_path.unlink(missing_ok=True)
            logger.info(f"Auto-cleaned from server: {file_path.name}")
    except Exception as e:
        logger.warning(f"Could not auto-delete {file_path}: {e}")

def cleanup_stale_files():
    """Removes any orphaned temp or final clips older than 30 minutes."""
    cutoff = time.time() - (30 * 60)
    for folder in [FINAL_DIR, TEMP_DIR]:
        for p in folder.glob("*"):
            if p.is_file() and p.stat().st_mtime < cutoff:
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass

def execute_clip_job(job_id: str, req: ClipRequest):
    jobs[job_id]["status"] = "processing"
    filename = req.output_filename or f"clip_{job_id[:8]}.mp4"
    if not filename.endswith(".mp4"):
        filename += ".mp4"

    cleanup_stale_files()

    try:
        jobs[job_id]["logs"].append("Step 1: Starting media ingestion...")
        output_path = run_job(
            source_input=req.url,
            output_filename=filename,
            start_time=req.start_time,
            end_time=req.end_time,
            duration=req.duration,
            force_pillarbox=req.force_pillarbox
        )

        jobs[job_id]["filename"] = filename
        jobs[job_id]["file_size"] = output_path.stat().st_size
        jobs[job_id]["download_url"] = f"/api/clips/{filename}"
        jobs[job_id]["logs"].append("Video render completed successfully (1080x1920 @ 60 FPS).")

        # Optional Google Drive upload (if user explicitly enabled it)
        if req.upload_to_gdrive:
            jobs[job_id]["logs"].append("Uploading final clip to Google Drive...")
            try:
                gdrive_res = upload_file_to_drive(str(output_path), folder_id=req.gdrive_folder_id)
                jobs[job_id]["gdrive"] = gdrive_res
                if gdrive_res.get("success"):
                    jobs[job_id]["logs"].append(f"Google Drive upload succeeded: {gdrive_res.get('link')}")
                else:
                    jobs[job_id]["logs"].append(f"Google Drive upload skipped: {gdrive_res.get('error')}")
            except Exception as ge:
                logger.error(f"Google Drive error: {ge}")
                jobs[job_id]["gdrive"] = {"success": False, "error": str(ge)}
                jobs[job_id]["logs"].append(f"Google Drive upload skipped: {ge}")

        jobs[job_id]["status"] = "completed"

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["logs"].append(f"ERROR: {str(e)}")

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Universal AI Video Clipper</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; display: flex; flex-direction: column; align-items: center; }
            .container { max-width: 680px; width: 100%; background: #1e293b; border-radius: 12px; padding: 2rem; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
            h1 { color: #38bdf8; margin-top: 0; }
            label { display: block; margin: 1rem 0 0.4rem; font-weight: 600; font-size: 0.9rem; }
            input, select { width: 100%; padding: 0.75rem; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #fff; box-sizing: border-box; }
            button { margin-top: 1.5rem; width: 100%; padding: 0.85rem; border-radius: 6px; border: none; background: #38bdf8; color: #0f172a; font-weight: 700; font-size: 1rem; cursor: pointer; transition: 0.2s; }
            button:hover { background: #0284c7; color: #fff; }
            .status-box { margin-top: 1.5rem; padding: 1rem; border-radius: 8px; background: #0f172a; border: 1px solid #334155; display: none; }
            pre { font-size: 0.85rem; color: #94a3b8; overflow-x: auto; }
            .badge { display: inline-block; padding: 0.25rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
            .badge-success { background: #16a34a; color: white; }
            .badge-processing { background: #ca8a04; color: white; }
            .badge-failed { background: #dc2626; color: white; }
            .btn-download { display: inline-block; padding: 0.75rem 1.25rem; background: #38bdf8; color: #0f172a; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 0.5rem; transition: 0.2s; }
            .btn-download:hover { background: #0284c7; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Universal AI Video Clipper</h1>
            <p style="color: #94a3b8;">Create 9:16 viral vertical Shorts directly from YouTube VODs/Streams with AI face-tracking and Hormozi karaoke captions.</p>
            <p style="color: #38bdf8; font-size: 0.85rem; background: #0f172a; padding: 0.6rem; border-radius: 6px; border-left: 3px solid #38bdf8;">
                ⚡ <b>Direct Download Enabled:</b> Clips stream straight to your device and auto-delete from server storage immediately after download.
            </p>
            
            <form id="clipForm">
                <label for="url">YouTube URL</label>
                <input type="text" id="url" required placeholder="https://www.youtube.com/watch?v=...">
                
                <div style="display: flex; gap: 1rem;">
                    <div style="flex: 1;">
                        <label for="start">Start Time (sec or HH:MM:SS)</label>
                        <input type="text" id="start" placeholder="e.g. 04:26.0">
                    </div>
                    <div style="flex: 1;">
                        <label for="end">End Time (sec or HH:MM:SS)</label>
                        <input type="text" id="end" placeholder="e.g. 05:15.0">
                    </div>
                </div>

                <label style="display: flex; align-items: center; gap: 0.5rem; margin-top: 1.2rem; cursor: pointer;">
                    <input type="checkbox" id="gdrive" style="width: auto;">
                    Also upload a backup copy to Google Drive
                </label>

                <button type="submit" id="submitBtn">Generate Viral Short 🚀</button>
            </form>

            <div class="status-box" id="statusBox">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>Job Status: <span id="statusBadge" class="badge"></span></strong>
                    <span id="jobIdText" style="font-size: 0.8rem; color: #64748b;"></span>
                </div>
                <div id="resultLinks" style="margin-top: 1rem;"></div>
                <pre id="logOutput"></pre>
            </div>
        </div>

        <script>
            const form = document.getElementById('clipForm');
            const submitBtn = document.getElementById('submitBtn');
            const statusBox = document.getElementById('statusBox');
            const statusBadge = document.getElementById('statusBadge');
            const jobIdText = document.getElementById('jobIdText');
            const resultLinks = document.getElementById('resultLinks');
            const logOutput = document.getElementById('logOutput');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                submitBtn.disabled = true;
                submitBtn.innerText = "Submitting job...";
                statusBox.style.display = "block";
                resultLinks.innerHTML = "";
                logOutput.innerText = "Queueing clipping pipeline...";

                try {
                    const res = await fetch('/api/clip', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            url: document.getElementById('url').value,
                            start_time: document.getElementById('start').value || null,
                            end_time: document.getElementById('end').value || null,
                            upload_to_gdrive: document.getElementById('gdrive').checked
                        })
                    });
                    const data = await res.json();
                    pollJob(data.job_id);
                } catch (err) {
                    logOutput.innerText = "Error: " + err;
                    submitBtn.disabled = false;
                    submitBtn.innerText = "Generate Viral Short 🚀";
                }
            });

            async function pollJob(jobId) {
                jobIdText.innerText = "ID: " + jobId;
                const interval = setInterval(async () => {
                    const res = await fetch('/api/jobs/' + jobId);
                    const job = await res.json();

                    statusBadge.innerText = job.status.toUpperCase();
                    statusBadge.className = "badge badge-" + (job.status === 'completed' ? 'success' : job.status === 'failed' ? 'failed' : 'processing');
                    logOutput.innerText = (job.logs || []).join("\\n");

                    if (job.status === 'completed') {
                        clearInterval(interval);
                        submitBtn.disabled = false;
                        submitBtn.innerText = "Generate Another Clip 🚀";
                        let html = `<p>✅ <b>Render Complete! (1080x1920 @ 60 FPS)</b></p>`;
                        html += `<p><a href="${job.download_url}" download class="btn-download">⬇️ Direct Download ${job.filename} (${(job.file_size / 1e6).toFixed(2)} MB)</a></p>`;
                        html += `<p style="font-size:0.8rem;color:#94a3b8;">* File automatically cleans up from server memory once downloaded.</p>`;
                        if (job.gdrive && job.gdrive.link) {
                            html += `<p><a href="${job.gdrive.link}" target="_blank" style="color:#4ade80;font-weight:bold;">📁 View backup in Google Drive</a></p>`;
                        }
                        resultLinks.innerHTML = html;
                    } else if (job.status === 'failed') {
                        clearInterval(interval);
                        submitBtn.disabled = false;
                        submitBtn.innerText = "Generate Viral Short 🚀";
                    }
                }, 3000);
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/clip")
def create_clip_job(req: ClipRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "url": req.url,
        "logs": ["Job queued."],
        "created_at": str(asyncio.get_event_loop().time())
    }
    background_tasks.add_task(execute_clip_job, job_id, req)
    return {"job_id": job_id, "status": "queued"}

@app.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/api/jobs")
def list_jobs():
    return list(jobs.values())

@app.get("/api/clips/{filename}")
def download_clip(filename: str, background_tasks: BackgroundTasks, keep_server_copy: bool = Query(False)):
    """
    Directly streams and downloads the 1080x1920 MP4 video to user device.
    By default (keep_server_copy=False), automatically unlinks/deletes the video
    from the server disk right after sending to preserve 0 MB server storage.
    """
    file_path = FINAL_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found or already downloaded and cleaned up.")

    if not keep_server_copy:
        # Schedule deletion right after the response completes
        background_tasks.add_task(auto_delete_file, file_path)

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename
    )

@app.post("/api/jobs/{job_id}/upload-gdrive")
def upload_existing_job_to_gdrive(job_id: str, folder_id: Optional[str] = None):
    if job_id not in jobs or jobs[job_id].get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job is not completed")
    filename = jobs[job_id].get("filename")
    file_path = FINAL_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File no longer exists on server")
    res = upload_file_to_drive(str(file_path), folder_id=folder_id)
    jobs[job_id]["gdrive"] = res
    return res

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
