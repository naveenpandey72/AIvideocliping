#!/usr/bin/env python3
"""
ingest.py - Universal Video Ingestion Module
Handles local file paths and YouTube URLs via yt-dlp.
Merges best video (up to 1080p) + best audio into an MP4 container with robust retry logic.
"""

import os
import sys
import time
import shutil
import logging
import argparse
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Ingest")

def ensure_ffmpeg():
    """Ensures FFmpeg binary path is discoverable and in environment."""
    ffmpeg_cmd = shutil.which("ffmpeg")
    if not ffmpeg_cmd:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        winget_dir = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_dir.exists():
            for p in winget_dir.glob("**/ffmpeg-*-full_build/bin"):
                if (p / "ffmpeg.exe").exists():
                    os.environ["PATH"] = str(p) + os.pathsep + os.environ.get("PATH", "")
                    return str(p)
    return str(Path(ffmpeg_cmd).parent) if ffmpeg_cmd else ""

def ingest_video(
    source: str,
    output_path: Path,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    duration: Optional[float] = None,
    max_retries: int = 3
) -> Path:
    """Ingests a video source (URL or local path) into an MP4 file."""
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_dir = ensure_ffmpeg()

    # Case A: Local File
    if os.path.exists(source):
        logger.info(f"Ingesting local file: {source}")
        source_path = Path(source).resolve()
        if source_path == output_path:
            return output_path

        # If clipping window requested
        if start_time is not None or duration is not None or end_time is not None:
            import subprocess
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
            if start_time is not None:
                cmd.extend(["-ss", str(start_time)])
            if end_time is not None:
                cmd.extend(["-to", str(end_time)])
            elif duration is not None:
                cmd.extend(["-t", str(duration)])
            cmd.extend([
                "-i", str(source_path),
                "-filter_complex", "[0:v]setpts=PTS-STARTPTS[v];[0:a]asetpts=PTS-STARTPTS[a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                str(output_path)
            ])
            subprocess.run(cmd, check=True)
        else:
            shutil.copy2(source_path, output_path)
        logger.info(f"Local ingestion complete: {output_path}")
        return output_path

    # Case B: YouTube or Remote URL
    import yt_dlp
    logger.info(f"Ingesting remote stream from: {source}")

    ydl_opts = {
        "format": "bestvideo[height<=2160]+bestaudio/bestvideo+bestaudio/best",
        "outtmpl": str(output_path.with_suffix(".part.%(ext)s")),
        "merge_output_format": "mp4",
        "quiet": False,
        "no_warnings": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        }
    }
    if ffmpeg_dir:
        ydl_opts["ffmpeg_location"] = ffmpeg_dir

    if start_time is not None and (end_time is not None or duration is not None):
        e_time = end_time if end_time is not None else (start_time + duration)
        ydl_opts["download_ranges"] = yt_dlp.utils.download_range_func([], [[start_time, e_time]])
        ydl_opts["force_keyframes_at_cuts"] = True

    for attempt in range(1, max_retries + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([source])
            break
        except Exception as e:
            logger.warning(f"Download attempt {attempt}/{max_retries} failed: {e}")
            if attempt == max_retries:
                raise
            time.sleep(2 * attempt)

    # Locate and rename the output file
    candidates = list(output_path.parent.glob(f"{output_path.stem}.part.*"))
    if not candidates:
        # Check if direct mp4 was created
        if output_path.exists():
            return output_path
        raise FileNotFoundError(f"Failed to find downloaded file for {source}")

    downloaded = candidates[0]
    if downloaded != output_path:
        if output_path.exists():
            output_path.unlink()
        downloaded.rename(output_path)

    logger.info(f"Ingestion successful: {output_path} ({output_path.stat().st_size} bytes)")
    return output_path

def parse_time(val: Optional[str]) -> Optional[float]:
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        parts = val.split(":")
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest video from URL or local file")
    parser.add_argument("--input", "-i", required=True, help="Video URL or local file path")
    parser.add_argument("--output", "-o", default="./temp_work/source.mp4", help="Output MP4 path")
    parser.add_argument("--start", help="Start time (seconds or HH:MM:SS)")
    parser.add_argument("--end", help="End time (seconds or HH:MM:SS)")
    parser.add_argument("--duration", type=float, help="Duration in seconds")
    args = parser.parse_args()

    s = parse_time(args.start)
    e = parse_time(args.end)
    out = ingest_video(
        source=args.input,
        output_path=Path(args.output),
        start_time=s,
        end_time=e,
        duration=args.duration
    )
    print(f"SUCCESS: {out}")
