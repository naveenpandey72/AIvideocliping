#!/usr/bin/env python3
"""
render_captions.py - Viral Karaoke Subtitle Generator & Burn-in Engine
Generates animated ASS karaoke subtitles:
  - 2-4 words per phrase
  - Bold sans-serif font (Impact / Arial Black / Montserrat)
  - Thick black stroke (\bord6\shad3)
  - Active spoken word highlighted in Gold/Electric Yellow (#FFD700 / &H0000D7FF&) with scale pop (\fscx112\fscy112)
  - Safe vertical margin (MarginV=280, Alignment=2) to avoid YouTube Shorts / TikTok UI buttons
Burns subtitles into the final 1080x1920 H.264 deliverable (CRF 20, AAC 192k).
"""

import os
import sys
import json
import shutil
import logging
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

import pysubs2
from pysubs2 import SSAFile, SSAEvent, SSAStyle, Color

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RenderCaptions")

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

def ms_to_ass_time(ms: int) -> str:
    """Converts milliseconds to ASS timestamp H:MM:SS.cs."""
    centis = int(round((ms % 1000) / 10.0))
    secs = int((ms // 1000) % 60)
    mins = int((ms // (1000 * 60)) % 60)
    hours = int(ms // (1000 * 60 * 60))
    if centis >= 100:
        secs += 1
        centis = 0
        if secs >= 60:
            mins += 1
            secs = 0
            if mins >= 60:
                hours += 1
                mins = 0
    return f"{hours}:{mins:02d}:{secs:02d}.{centis:02d}"

def generate_karaoke_ass(
    transcript_json: Path,
    output_ass: Path,
    words_per_phrase: int = 3,
    font_name: str = "Impact",
    font_size: int = 72,
    margin_v: int = 280,
    active_color_ass: str = "&H0000D7FF&"  # #FFD700 in BGR hex format
) -> Path:
    """Creates a high-retention word-by-word karaoke ASS file."""
    with open(transcript_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Flatten all words with start/end
    flat_words = []
    for seg in data.get("segments", []):
        for w in seg.get("words", []):
            flat_words.append({
                "word": w["word"].strip().upper(),
                "start_ms": int(w["start"] * 1000),
                "end_ms": int(w["end"] * 1000)
            })

    # Group into dynamic chunks
    phrases = []
    curr_phrase = []
    for i, w in enumerate(flat_words):
        curr_phrase.append(w)
        is_last = (i == len(flat_words) - 1)
        long_pause = (not is_last and (flat_words[i + 1]["start_ms"] - w["end_ms"] > 400))
        if len(curr_phrase) >= words_per_phrase or long_pause or is_last:
            phrases.append(curr_phrase)
            curr_phrase = []

    # Write ASS script header with standard styling
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ViralKaraoke,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,3,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for group in phrases:
        if not group:
            continue
        for active_idx, target in enumerate(group):
            w_start = target["start_ms"]
            w_end = target["end_ms"]
            if active_idx < len(group) - 1:
                w_end = min(w_end, group[active_idx + 1]["start_ms"])
            if w_end <= w_start:
                w_end = w_start + 100

            start_str = ms_to_ass_time(w_start)
            end_str = ms_to_ass_time(w_end)

            words_markup = []
            for j, item in enumerate(group):
                word_text = item["word"]
                if j == active_idx:
                    words_markup.append(f"{{\\c{active_color_ass}\\fscx112\\fscy112}}{word_text}{{\\c&H00FFFFFF&\\fscx100\\fscy100}}")
                else:
                    words_markup.append(word_text)

            line_text = " ".join(words_markup)
            events.append(f"Dialogue: 0,{start_str},{end_str},ViralKaraoke,,0,0,0,,{line_text}")

    output_ass.parent.mkdir(parents=True, exist_ok=True)
    with open(output_ass, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

    logger.info(f"Generated ASS karaoke subtitles: {len(events)} events -> {output_ass}")
    return output_ass

def burn_captions_to_video(
    video_path: Path,
    ass_path: Path,
    output_video: Path
) -> Path:
    """Burns ASS subtitles into 1080x1920 video using FFmpeg libass."""
    ffmpeg_cmd = ensure_ffmpeg()
    output_video = Path(output_video).resolve()
    output_video.parent.mkdir(parents=True, exist_ok=True)

    escaped_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    cmd = [
        ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path),
        "-vf", f"ass='{escaped_ass}'",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-r", "60",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_video)
    ]
    logger.info(f"Burning subtitles into {output_video}...")
    subprocess.run(cmd, check=True)
    logger.info(f"Burn-in complete: {output_video}")
    return output_video

def render_short_deliverable(
    cropped_video: Path,
    transcript_json: Path,
    final_output: Path,
    words_per_phrase: int = 3,
    margin_v: int = 280
) -> Path:
    """Generates ASS and burns into final MP4 deliverable."""
    temp_ass = final_output.parent / f"temp_{final_output.stem}.ass"
    try:
        generate_karaoke_ass(
            transcript_json=transcript_json,
            output_ass=temp_ass,
            words_per_phrase=words_per_phrase,
            margin_v=margin_v
        )
        burn_captions_to_video(
            video_path=cropped_video,
            ass_path=temp_ass,
            output_video=final_output
        )
        return final_output
    finally:
        if temp_ass.exists():
            try:
                temp_ass.unlink()
            except Exception:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render viral karaoke subtitles on video")
    parser.add_argument("--video", "-v", required=True, help="Cropped 1080x1920 video")
    parser.add_argument("--transcript", "-t", required=True, help="Transcript JSON with word timings")
    parser.add_argument("--output", "-o", required=True, help="Final deliverable MP4 path")
    parser.add_argument("--margin-v", type=int, default=280, help="Bottom margin safe zone (default: 280)")
    parser.add_argument("--words-per-phrase", type=int, default=3, help="Words per subtitle line (default: 3)")
    args = parser.parse_args()

    out = render_short_deliverable(
        cropped_video=Path(args.video),
        transcript_json=Path(args.transcript),
        final_output=Path(args.output),
        words_per_phrase=args.words_per_phrase,
        margin_v=args.margin_v
    )
    print(f"SUCCESS: {out}")
