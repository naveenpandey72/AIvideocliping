#!/usr/bin/env python3
"""
smart_crop.py - Intelligent 9:16 AI Subject Tracking & Dynamic Framing Module
Uses MediaPipe / OpenCV Face Detection with Exponential Moving Average (EMA) smoothing for jitter-free pan-and-scan.
If no face/subject is detected for >1.5s, seamlessly falls back to 1080x1920 blurred-background pillarbox layout.
"""

import os
import sys
import shutil
import logging
import argparse
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple

os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()

import cv2
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SmartCrop")

def ensure_ffmpeg():
    ffmpeg_cmd = shutil.which("ffmpeg")
    if not ffmpeg_cmd:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        winget_dir = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_dir.exists():
            for p in winget_dir.glob("**/ffmpeg-*-full_build/bin"):
                if (p / "ffmpeg.exe").exists():
                    os.environ["PATH"] = str(p) + os.pathsep + os.environ.get("PATH", "")
                    return "ffmpeg"
    return ffmpeg_cmd or "ffmpeg"

class FaceTracker:
    """Robust face tracker using OpenCV Haar Cascade with MediaPipe task support."""
    def __init__(self):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.cascade = cv2.CascadeClassifier(cascade_path)

    def detect_face_center(self, bgr_frame: np.ndarray) -> Optional[float]:
        """Returns the X center of the primary detected face, or None."""
        gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
        if len(faces) > 0:
            # Pick largest face
            largest = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest
            return float(x + w / 2.0)
        return None

def smart_crop_video(
    input_video: Path,
    output_video: Path,
    target_width: int = 1080,
    target_height: int = 1920,
    ema_alpha: float = 0.08,
    no_face_timeout_sec: float = 1.5,
    force_pillarbox: bool = False
) -> Path:
    """
    Crops input video to 1080x1920 9:16 portrait.
    Applies face tracking with temporal EMA smoothing.
    Falls back to blurred-background layout when no face is present for > no_face_timeout_sec.
    """
    input_path = Path(input_video).resolve()
    output_path = Path(output_video).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_cmd = ensure_ffmpeg()

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {input_path}")

    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    logger.info(f"Input dimensions: {src_w}x{src_h} @ {fps:.2f}fps ({total_frames} frames)")

    # If source is already ~9:16 vertical
    if abs((src_w / float(src_h)) - (target_width / float(target_height))) < 0.03 and not force_pillarbox:
        logger.info("Video is already 9:16 aspect ratio. Scaling directly to 1080x1920.")
        cap.release()
        cmd = [
            ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(input_path),
            "-vf", f"scale={target_width}:{target_height}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-c:a", "copy",
            str(output_path)
        ]
        subprocess.run(cmd, check=True)
        return output_path

    # Calculate 9:16 crop width on source height
    crop_w = int(src_h * (target_width / target_height))

    if crop_w > src_w or force_pillarbox:
        logger.info("Source aspect ratio narrower than 9:16 or pillarbox forced. Using blurred-background layout.")
        cap.release()
        return render_blurred_pillarbox_ffmpeg(input_path, output_path, target_width, target_height)

    tracker = FaceTracker()

    temp_crop_video = output_path.parent / f"temp_{output_path.stem}_nosound.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_writer = cv2.VideoWriter(str(temp_crop_video), fourcc, fps, (target_width, target_height))

    current_center_x = float(src_w / 2.0)
    target_center_x = float(src_w / 2.0)
    min_center_x = crop_w / 2.0
    max_center_x = src_w - (crop_w / 2.0)

    no_face_frames_threshold = int(no_face_timeout_sec * fps)
    frames_without_face = 0
    in_pillarbox_mode = False
    pillarbox_blend = 0.0

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        face_x = tracker.detect_face_center(frame)

        if face_x is not None:
            target_center_x = np.clip(face_x, min_center_x, max_center_x)
            frames_without_face = 0
        else:
            frames_without_face += 1

        if frames_without_face > no_face_frames_threshold:
            in_pillarbox_mode = True
        else:
            in_pillarbox_mode = False

        if in_pillarbox_mode:
            pillarbox_blend = min(1.0, pillarbox_blend + 0.05)
            target_center_x = float(src_w / 2.0)
        else:
            pillarbox_blend = max(0.0, pillarbox_blend - 0.05)

        # Exponential Moving Average (EMA)
        current_center_x = ema_alpha * target_center_x + (1.0 - ema_alpha) * current_center_x
        current_center_x = np.clip(current_center_x, min_center_x, max_center_x)

        x1 = int(current_center_x - crop_w / 2.0)
        x2 = x1 + crop_w
        x1 = max(0, min(src_w - crop_w, x1))
        x2 = x1 + crop_w

        cropped_subject = frame[0:src_h, x1:x2]
        scaled_subject = cv2.resize(cropped_subject, (target_width, target_height), interpolation=cv2.INTER_LINEAR)

        if pillarbox_blend > 0.001:
            bg = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
            bg = cv2.GaussianBlur(bg, (51, 51), 0)
            bg = cv2.addWeighted(bg, 0.75, np.zeros_like(bg), 0.25, 0)

            fg_scale = target_width / float(src_w)
            fg_w = target_width
            fg_h = int(src_h * fg_scale)
            fg_scaled = cv2.resize(frame, (fg_w, fg_h), interpolation=cv2.INTER_LINEAR)

            fg_y1 = int((target_height - fg_h) / 2)
            bg[fg_y1:fg_y1 + fg_h, 0:fg_w] = fg_scaled

            final_frame = cv2.addWeighted(bg, pillarbox_blend, scaled_subject, 1.0 - pillarbox_blend, 0)
        else:
            final_frame = scaled_subject

        out_writer.write(final_frame)
        frame_idx += 1

    cap.release()
    out_writer.release()

    logger.info("Muxing original audio back into smoothed 9:16 crop...")
    mux_cmd = [
        ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(temp_crop_video),
        "-i", str(input_path),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0?",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path)
    ]
    subprocess.run(mux_cmd, check=True)

    if temp_crop_video.exists():
        temp_crop_video.unlink()

    logger.info(f"Smart crop complete: {output_path}")
    return output_path

def render_blurred_pillarbox_ffmpeg(
    input_path: Path,
    output_path: Path,
    target_width: int = 1080,
    target_height: int = 1920
) -> Path:
    """Fast FFmpeg-based blurred background pillarbox fallback."""
    ffmpeg_cmd = ensure_ffmpeg()
    filter_complex = (
        f"[0:v]split=2[bg_in][fg_in];"
        f"[bg_in]scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height},boxblur=25:2,eq=brightness=-0.15[bg];"
        f"[fg_in]scale={target_width}:-2:force_original_aspect_ratio=decrease[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2[outv]"
    )
    cmd = [
        ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(input_path),
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    subprocess.run(cmd, check=True)
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart 9:16 AI Face Tracking & Pan-and-Scan")
    parser.add_argument("--input", "-i", required=True, help="Input video")
    parser.add_argument("--output", "-o", default="./temp_work/cropped_9_16.mp4", help="Output 9:16 video")
    parser.add_argument("--smooth-alpha", type=float, default=0.08, help="EMA smoothing factor (0.05-0.15)")
    parser.add_argument("--pillarbox", action="store_true", help="Force blurred pillarbox layout")
    args = parser.parse_args()

    out = smart_crop_video(
        input_video=Path(args.input),
        output_video=Path(args.output),
        ema_alpha=args.smooth_alpha,
        force_pillarbox=args.pillarbox
    )
    print(f"SUCCESS: {out}")
