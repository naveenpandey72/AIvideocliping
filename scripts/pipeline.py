#!/usr/bin/env python3
"""
pipeline.py - Autonomous End-to-End Pipeline Orchestrator
Executes the complete Universal Clipper pipeline:
  1. Ingestion (URL or local) -> temp_work/
  2. Audio Extraction & Word-level Transcription
  3. AI Face Tracking & Smart Cropping to 1080x1920
  4. ASS Karaoke Caption Generation & Burn-in
  5. Verification & Cleanup -> final_clips/
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Pipeline")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp_work"
FINAL_DIR = BASE_DIR / "final_clips"
SCRIPTS_DIR = BASE_DIR / "scripts"

def run_job(
    source_input: str,
    output_filename: str = "viral_short.mp4",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    duration: Optional[float] = None,
    model_name: str = "base",
    force_pillarbox: bool = False
) -> Path:
    """Executes the full pipeline for a designated clip segment."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)

    slug = Path(output_filename).stem
    slice_path = TEMP_DIR / f"{slug}_ingest.mp4"
    transcript_path = TEMP_DIR / f"{slug}_transcript.json"
    cropped_path = TEMP_DIR / f"{slug}_cropped.mp4"
    final_output = FINAL_DIR / output_filename

    python_bin = sys.executable

    logger.info("==================================================")
    logger.info(f"STARTING UNIVERSAL CLIPPER JOB: {output_filename}")
    logger.info("==================================================")

    # 1. Ingest
    logger.info("--- Step 1/4: Ingesting Media ---")
    ingest_cmd = [
        python_bin, str(SCRIPTS_DIR / "ingest.py"),
        "--input", source_input,
        "--output", str(slice_path)
    ]
    if start_time:
        ingest_cmd.extend(["--start", str(start_time)])
    if end_time:
        ingest_cmd.extend(["--end", str(end_time)])
    elif duration:
        ingest_cmd.extend(["--duration", str(duration)])
    subprocess.run(ingest_cmd, check=True)

    # 2. Transcribe
    logger.info("--- Step 2/4: Transcribing Audio with Word Timestamps ---")
    transcribe_cmd = [
        python_bin, str(SCRIPTS_DIR / "transcribe.py"),
        "--input", str(slice_path),
        "--output", str(transcript_path),
        "--model", model_name
    ]
    subprocess.run(transcribe_cmd, check=True)

    # 3. Smart Crop to 1080x1920
    logger.info("--- Step 3/4: MediaPipe AI Face Tracking & 9:16 Cropping ---")
    crop_cmd = [
        python_bin, str(SCRIPTS_DIR / "smart_crop.py"),
        "--input", str(slice_path),
        "--output", str(cropped_path)
    ]
    if force_pillarbox:
        crop_cmd.append("--pillarbox")
    subprocess.run(crop_cmd, check=True)

    # 4. Render Captions
    logger.info("--- Step 4/4: Burning Viral Karaoke Captions ---")
    caption_cmd = [
        python_bin, str(SCRIPTS_DIR / "render_captions.py"),
        "--video", str(cropped_path),
        "--transcript", str(transcript_path),
        "--output", str(final_output)
    ]
    subprocess.run(caption_cmd, check=True)

    # 5. Verification
    if not final_output.exists() or final_output.stat().st_size == 0:
        raise RuntimeError(f"Deliverable generation failed: {final_output}")

    logger.info("==================================================")
    logger.info(f"SUCCESS: Deliverable ready at {final_output}")
    logger.info(f"File Size: {final_output.stat().st_size:,} bytes")
    logger.info("==================================================")

    # 6. Ephemeral cleanup of temp files for this job
    for f in [slice_path, transcript_path, cropped_path]:
        if f.exists():
            try:
                f.unlink()
            except Exception:
                pass

    return final_output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run autonomous vertical video clipping job")
    parser.add_argument("--input", "-i", required=True, help="Video URL or local file path")
    parser.add_argument("--output", "-o", default="viral_clip_01.mp4", help="Output MP4 filename in final_clips/")
    parser.add_argument("--start", help="Start timestamp (HH:MM:SS or seconds)")
    parser.add_argument("--end", help="End timestamp (HH:MM:SS or seconds)")
    parser.add_argument("--duration", type=float, help="Clip duration in seconds")
    parser.add_argument("--model", default="base", help="Whisper model (tiny, base, small)")
    parser.add_argument("--pillarbox", action="store_true", help="Force blurred pillarbox layout")
    args = parser.parse_args()

    run_job(
        source_input=args.input,
        output_filename=args.output,
        start_time=args.start,
        end_time=args.end,
        duration=args.duration,
        model_name=args.model,
        force_pillarbox=args.pillarbox
    )
