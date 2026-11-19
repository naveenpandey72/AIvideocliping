# 🎬 Universal AI Video Clipper

An autonomous video clipping engine that ingests YouTube VODs/streams, automatically isolates high-retention viral moments, applies smooth AI face tracking / 9:16 vertical crop, burns Hormozi-style animated karaoke subtitles, and exports 1080x1920 @ 60 FPS ready-to-post Shorts.

---

## 🚀 One-Click Deploy on Render.com

This repository is pre-configured with a production-ready `Dockerfile` and `render.yaml`.

### Step 1: Connect to Render
1. Go to [Render.com Dashboard](https://dashboard.render.com).
2. Click **New +** > **Web Service**.
3. Select **Build and deploy from a Git repository** and connect:
   `https://github.com/naveenpandey72/AIvideocliping`
4. Choose **Docker** as the Runtime (or select the Blueprint if prompted).
5. **Instance Type:** Select **Starter** or **Standard** (at least 1GB–2GB RAM is required for Whisper AI transcription + FFmpeg encoding).

### Step 2: Add Google Drive Service Account (Secret)
Because this repository is public, **never commit `service_account.json` to GitHub**. Instead, configure it in Render:

**Method A: Secret File (Recommended)**
1. In your Render Web Service dashboard, go to the **Environment** tab.
2. Scroll to **Secret Files** and click **Add Secret File**.
3. Filename: `service_account.json`
4. Contents: Paste the entire JSON content of your `service_account.json`.

**Method B: Environment Variable**
1. Add an Environment Variable named `GDRIVE_SERVICE_ACCOUNT_JSON`.
2. Paste the raw JSON string as the value.

---

## 🌐 API & Web UI

### Web Interface
Navigate to your deployed Render URL (e.g., `https://your-app.onrender.com/`) in your browser to use the interactive dashboard:
- Enter any YouTube URL.
- Specify start and end timestamps.
- Enable automatic upload to Google Drive.
- Track real-time progress and download the 1080x1920 MP4 directly.

### REST API Endpoints

#### 1. Trigger Clip Job
`POST /api/clip`
```json
{
  "url": "https://www.youtube.com/watch?v=M4f-4ucxtEU",
  "start_time": "04:26.0",
  "end_time": "05:15.0",
  "upload_to_gdrive": true
}
```
**Response:**
```json
{
  "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "queued"
}
```

#### 2. Poll Status
`GET /api/jobs/{job_id}`
```json
{
  "job_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "completed",
  "filename": "clip_9b1deb4d.mp4",
  "file_size": 35409567,
  "download_url": "/api/clips/clip_9b1deb4d.mp4",
  "gdrive": {
    "link": "https://drive.google.com/file/d/..."
  }
}
```

#### 3. Direct Download
`GET /api/clips/{filename}`
Streams and downloads the rendered MP4 file directly.

---

## 🛠️ Local Development

```bash
# Clone the repository
git clone https://github.com/naveenpandey72/AIvideocliping.git
cd AIvideocliping

# Create virtual environment & install requirements
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI app
python app.py
```
Visit `http://localhost:8000` in your browser.
