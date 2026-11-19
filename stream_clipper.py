#!/usr/bin/env python3
"""
Stream Clipper: Viral 9:16 Shorts Generation Pipeline
Native Python/FFmpeg implementation adhering strictly to:
  - Rule A: Zero Audio-Video Drift (DASH Sync)
  - Rule B: Viral Framing Formula (Facecam TOP + 3:4 Gameplay DOWN)
  - Rule C: Word-by-Word Hormozi Karaoke Subtitles (ASS)
  - Rule D: Mandatory Workspace Cleanup
"""

import os
import sys
import json
import shutil
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("StreamClipper")

# ---------------------------------------------------------
# PATH & ENVIRONMENT RESOLUTION
# ---------------------------------------------------------
def ensure_ffmpeg_in_path() -> Tuple[str, str]:
    """Ensures ffmpeg and ffprobe are discoverable, checking standard Windows winget paths."""
    ffmpeg_cmd = shutil.which("ffmpeg")
    ffprobe_cmd = shutil.which("ffprobe")

    if not ffmpeg_cmd or not ffprobe_cmd:
        # Check standard Gyan.FFmpeg installation directory
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        winget_ffmpeg_dir = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_ffmpeg_dir.exists():
            for p in winget_ffmpeg_dir.glob("**/ffmpeg-*-full_build/bin"):
                candidate_ffmpeg = p / "ffmpeg.exe"
                candidate_ffprobe = p / "ffprobe.exe"
                if candidate_ffmpeg.exists() and candidate_ffprobe.exists():
                    os.environ["PATH"] = str(p) + os.pathsep + os.environ.get("PATH", "")
                    ffmpeg_cmd = str(candidate_ffmpeg)
                    ffprobe_cmd = str(candidate_ffprobe)
                    logger.info(f"Discovered FFmpeg in WinGet package directory: {p}")
                    break

    if not ffmpeg_cmd or not ffprobe_cmd:
        raise RuntimeError("FFmpeg or FFprobe could not be located in PATH. Please install Gyan.FFmpeg via winget.")

    return ffmpeg_cmd, ffprobe_cmd


def check_gpu_encoder() -> Tuple[str, str]:
    """Determines whether NVIDIA NVENC (h264_nvenc) or CPU (libx264) should be used."""
    ffmpeg_cmd, _ = ensure_ffmpeg_in_path()
    test_cmd = [
        ffmpeg_cmd, "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "testsrc=duration=1:size=640x360:rate=30",
        "-c:v", "h264_nvenc", "-f", "null", "-"
    ]
    try:
        res = subprocess.run(test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            logger.info("Hardware Acceleration: NVIDIA NVENC (h264_nvenc) available.")
            return "h264_nvenc", "-preset p4"
    except Exception:
        pass

    logger.info("Hardware Acceleration: NVIDIA GPU not detected / NVENC unavailable. Falling back to CPU: libx264 -preset veryfast")
    return "libx264", "-preset veryfast"


# ---------------------------------------------------------
# SUBTITLE GENERATION (RULE C: HORMOZI KARAOKE ASS)
# ---------------------------------------------------------
def format_ass_time(seconds: float) -> str:
    """Converts seconds into ASS format timestamp (H:MM:SS.cs)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        secs += 1
        centis = 0
        if secs >= 60:
            minutes += 1
            secs = 0
            if minutes >= 60:
                hours += 1
                minutes = 0
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def build_hormozi_ass_subtitles(
    segments,
    output_ass_path: Path,
    words_per_group: int = 3,
    y_pos: int = 620
) -> Path:
    """
    Generates word-by-word animated ASS karaoke subtitles:
      - Font: Impact / Montserrat ExtraBold (Uppercase, Fontsize 72)
      - Text: White (&H00FFFFFF&) with heavy black outline (\\bord6\\shad3)
      - Active word pops in Electric Yellow (&H00E5FF&) with scale pop (\\fscx115\\fscy115)
      - Centered at \\pos(540, y_pos) below facecam seam
    """
    all_words = []
    for s in segments:
        if hasattr(s, "words") and s.words:
            for w in s.words:
                all_words.append({
                    "word": w.word.strip().upper(),
                    "start": max(0.0, w.start),
                    "end": max(w.start + 0.05, w.end)
                })

    # Group words into short dynamic chunks
    groups = []
    curr_group = []
    for i, w in enumerate(all_words):
        curr_group.append(w)
        # Split on max count or speech pause > 0.4s
        is_last = (i == len(all_words) - 1)
        long_pause = (not is_last and (all_words[i + 1]["start"] - w["end"] > 0.4))
        if len(curr_group) >= words_per_group or long_pause or is_last:
            groups.append(curr_group)
            curr_group = []

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,Impact,72,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,3,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for group in groups:
        if not group:
            continue
        g_start = group[0]["start"]
        g_end = group[-1]["end"]

        for active_idx, target_word in enumerate(group):
            w_start = target_word["start"]
            w_end = target_word["end"]
            # If there's a next word in this group, clamp end time
            if active_idx < len(group) - 1:
                w_end = min(w_end, group[active_idx + 1]["start"])
            w_start_str = format_ass_time(w_start)
            w_end_str = format_ass_time(w_end)

            # Assemble line with active word highlighted in Electric Yellow with scale pop
            line_parts = []
            for j, w in enumerate(group):
                word_clean = w["word"]
                if j == active_idx:
                    # Pop active word in Electric Yellow (&H00E5FF&) with 115% scale
                    line_parts.append(f"{{\\c&H00E5FF&\\fscx115\\fscy115}}{word_clean}{{\\c&H00FFFFFF&\\fscx100\\fscy100}}")
                else:
                    line_parts.append(word_clean)

            spoken_text = " ".join(line_parts)
            dialogue = f"Dialogue: 0,{w_start_str},{w_end_str},Hormozi,,0,0,0,,{{\\pos(540,{y_pos})\\an5}}{spoken_text}"
            events.append(dialogue)

    ass_content = header + "\n".join(events) + "\n"
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_content)

    logger.info(f"Generated Hormozi ASS subtitles with {len(events)} word-pop events.")
    return output_ass_path


# ---------------------------------------------------------
# AUDIO TRANSCRIPTION (FASTER-WHISPER)
# ---------------------------------------------------------
def extract_audio_and_transcribe(
    video_path: Path,
    whisper_model_name: str = "base.en",
    temp_dir: Optional[Path] = None
) -> Tuple[list, Path]:
    """Extracts 16kHz mono audio from video and transcribes using faster-whisper with word timestamps."""
    ffmpeg_cmd, _ = ensure_ffmpeg_in_path()
    work_dir = temp_dir or video_path.parent
    temp_wav = work_dir / f"temp_{video_path.stem}_audio.wav"

    extract_cmd = [
        ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(temp_wav)
    ]
    subprocess.run(extract_cmd, check=True)

    try:
        from faster_whisper import WhisperModel
        logger.info(f"Loading faster-whisper model '{whisper_model_name}' on CPU (int8)...")
        model = WhisperModel(whisper_model_name, device="cpu", compute_type="int8")
        segments_generator, info = model.transcribe(
            str(temp_wav),
            word_timestamps=True,
            vad_filter=True,
            language="en"
        )
        segments = list(segments_generator)
        logger.info(f"Transcription complete: {len(segments)} segments transcribed.")
        return segments, temp_wav
    finally:
        if temp_wav.exists():
            try:
                temp_wav.unlink()
            except Exception:
                pass


# ---------------------------------------------------------
# STREAM CUTTING & ZERO DRIFT ALIGNMENT (RULE A)
# ---------------------------------------------------------
def cut_segment_with_zero_drift(
    input_source: str,
    output_sliced_path: Path,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    duration: Optional[float] = None
) -> Path:
    """
    Downloads or cuts a video slice ensuring zero DASH drift.
    Aligns presentation timestamps strictly to 0.000000 using setpts & asetpts.
    """
    ffmpeg_cmd, _ = ensure_ffmpeg_in_path()

    # If it is a remote stream URL (YouTube / Twitch)
    if input_source.startswith("http://") or input_source.startswith("https://"):
        import yt_dlp
        logger.info(f"Downloading stream segment from URL: {input_source}")
        ydl_opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "outtmpl": str(output_sliced_path.with_suffix(".raw.%(ext)s")),
            "quiet": True,
            "no_warnings": True,
        }
        if start_time and (end_time or duration):
            e_time = end_time if end_time else f"{float(start_time) + duration}"
            ydl_opts["download_ranges"] = yt_dlp.utils.download_range_func([], [[float(start_time), float(e_time)]])
            ydl_opts["force_keyframes_at_cuts"] = True

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([input_source])

        # Locate the downloaded file
        candidates = list(output_sliced_path.parent.glob(f"{output_sliced_path.stem}.raw.*"))
        if not candidates:
            raise FileNotFoundError(f"Failed to download video from {input_source}")
        raw_source = candidates[0]
    else:
        raw_source = Path(input_source)
        if not raw_source.exists():
            raise FileNotFoundError(f"Source video file not found: {raw_source}")

    # Re-encode and align PTS strictly to 0.000000s
    time_args = []
    if start_time:
        time_args.extend(["-ss", str(start_time)])
    if end_time:
        time_args.extend(["-to", str(end_time)])
    elif duration:
        time_args.extend(["-t", str(duration)])

    pts_filter = "[0:v]setpts=PTS-STARTPTS[v];[0:a]asetpts=PTS-STARTPTS[a]"
    cmd = [
        ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error"
    ] + time_args + [
        "-i", str(raw_source),
        "-filter_complex", pts_filter,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(output_sliced_path)
    ]
    subprocess.run(cmd, check=True)

    # Cleanup raw download if created
    if raw_source != Path(input_source) and raw_source.exists():
        try:
            raw_source.unlink()
        except Exception:
            pass

    logger.info(f"Extracted slice with Zero-Drift PTS reset: {output_sliced_path}")
    return output_sliced_path


# ---------------------------------------------------------
# VIRAL FRAMING FORMULA (RULE B) & ENCODING
# ---------------------------------------------------------
def render_viral_short(
    input_video: Path,
    output_short_path: Path,
    subtitles_ass_path: Optional[Path] = None,
    facecam_preset: str = "bottom-right",
    facecam_coords: Optional[Tuple[int, int, int, int]] = None
) -> Path:
    """
    Renders 1080x1920 (9:16 Vertical) canvas following Rule B:
      - Background: Ambient gameplay scaled to 1080x1920 with heavy Gaussian blur (boxblur=25:2) and slight darkness tint (brightness=-0.15)
      - TOP SPACE (Y = 0 to 480): Streamer Facecam enlarged and centered (approx 620x480)
      - CENTER / BOTTOM (Y = 480 to 1920): Gameplay cropped to 3:4 aspect ratio, scaled to 1080x1440. Zero black bars.
      - Burn-in ASS Subtitles positioned at \\pos(540,620)
    """
    ffmpeg_cmd, _ = ensure_ffmpeg_in_path()
    v_encoder, v_preset = check_gpu_encoder()

    # Determine facecam crop expression
    if facecam_coords:
        if isinstance(facecam_coords, str):
            crop_expr = facecam_coords
        else:
            fc_x, fc_y, fc_w, fc_h = facecam_coords
            crop_expr = f"{fc_w}:{fc_h}:{fc_x}:{fc_y}"
    else:
        preset_map = {
            "bottom-right": "480:360:1440:720",
            "bottom-left": "480:360:0:720",
            "top-right": "480:360:1440:0",
            "top-left": "480:360:0:0",
            "streamer-left": "iw*0.35:ih*0.75:iw*0.08:ih*0.17"
        }
        crop_expr = preset_map.get(facecam_preset, "480:360:1440:720")

    # Construct Filtergraph
    # 1. Reset PTS: [0:v]setpts=PTS-STARTPTS[v0];[0:a]asetpts=PTS-STARTPTS[a0]
    # 2. Background: ambient scale, crop 1080:1920, boxblur=25:2, eq=brightness=-0.15
    # 3. Gameplay: 3:4 aspect crop (ih*3/4), scaled to 1080x1440
    # 4. Facecam: crop from source, scaled to fit max 640x480 centered in top space
    # 5. Overlays: Gameplay at (0, 480); Facecam at ((1080-w)/2, (480-h)/2)
    # 6. ASS Subtitles burned into composite
    ass_filter = ""
    if subtitles_ass_path and subtitles_ass_path.exists():
        # Escape path for FFmpeg filtergraph on Windows (libass)
        escaped_ass = str(subtitles_ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
        ass_filter = f"[v_comp]ass='{escaped_ass}'[v_out];"
    else:
        ass_filter = "[v_comp]null[v_out];"

    filter_complex = (
        f"[0:v]setpts=PTS-STARTPTS[v_pts];[0:a]asetpts=PTS-STARTPTS[a_out];"
        f"[v_pts]split=3[bg_in][game_in][cam_in];"
        f"[bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2,eq=brightness=-0.15[bg];"
        f"[game_in]crop=ih*3/4:ih:(iw-ih*3/4)/2:0,scale=1080:1440[gameplay];"
        f"[cam_in]crop={crop_expr},scale=640:480:force_original_aspect_ratio=decrease[facecam];"
        f"[bg][gameplay]overlay=0:480[bg_game];"
        f"[bg_game][facecam]overlay=(W-w)/2:(480-h)/2[v_comp];"
        f"{ass_filter}"
    )

    encode_cmd = [
        ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(input_video),
        "-filter_complex", filter_complex,
        "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", v_encoder
    ] + v_preset.split() + [
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_short_path)
    ]

    logger.info(f"Rendering viral 9:16 short using {v_encoder}...")
    subprocess.run(encode_cmd, check=True)
    logger.info(f"Render complete: {output_short_path}")
    return output_short_path


# ---------------------------------------------------------
# MULTI-STAGE VERIFICATION
# ---------------------------------------------------------
def verify_pipeline_output(video_path: Path) -> Dict[str, any]:
    """
    Validates deliverable video against all architectural rules:
      - Resolution == 1080x1920 (Rule B)
      - Audio and Video start times == 0.000000s (Rule A)
      - Stream integrity & zero frame decode errors
    """
    _, ffprobe_cmd = ensure_ffmpeg_in_path()
    ffmpeg_cmd, _ = ensure_ffmpeg_in_path()

    probe_cmd = [
        ffprobe_cmd, "-v", "error",
        "-show_entries", "stream=index,codec_type,codec_name,width,height,start_time,duration",
        "-of", "json",
        str(video_path)
    ]
    result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    probe_data = json.loads(result.stdout.decode("utf-8"))

    streams = probe_data.get("streams", [])
    video_stream = next((s for s in streams if s["codec_type"] == "video"), None)
    audio_stream = next((s for s in streams if s["codec_type"] == "audio"), None)

    if not video_stream or not audio_stream:
        raise ValueError(f"Missing video or audio stream in output: {video_path}")

    v_start = float(video_stream.get("start_time", 0.0))
    a_start = float(audio_stream.get("start_time", 0.0))
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))

    # Verify zero-drift start timestamps
    pts_synced = (abs(v_start) < 0.001) and (abs(a_start) < 0.001)
    resolution_ok = (width == 1080 and height == 1920)

    # Frame decode health check
    decode_check = subprocess.run(
        [ffmpeg_cmd, "-v", "error", "-i", str(video_path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    no_decode_errors = (decode_check.returncode == 0 and len(decode_check.stderr) == 0)

    report = {
        "file": str(video_path),
        "resolution": f"{width}x{height}",
        "resolution_ok": resolution_ok,
        "video_start_time": f"{v_start:.6f}s",
        "audio_start_time": f"{a_start:.6f}s",
        "pts_zero_drift_synced": pts_synced,
        "decode_error_free": no_decode_errors,
        "all_checks_passed": pts_synced and resolution_ok and no_decode_errors
    }
    return report


# ---------------------------------------------------------
# WORKSPACE CLEANUP (RULE D)
# ---------------------------------------------------------
def clean_workspace(workspace_dir: Path, keep_files: List[Path]) -> None:
    """
    Deletes all temporary slices, frames (.jpg/.png), subtitles (.ass/.vtt),
    json logs, and scratch scripts.
    Preserves ONLY the final deliverable .mp4 files and the pipeline script.
    """
    keep_set = {f.resolve() for f in keep_files}
    pipeline_script = Path(__file__).resolve()
    keep_set.add(pipeline_script)

    deleted_count = 0
    for p in workspace_dir.glob("*"):
        if p.resolve() in keep_set:
            continue
        if p.is_file():
            if p.suffix.lower() in [".ass", ".vtt", ".json", ".wav", ".jpg", ".png", ".tmp", ".log"] or p.name.startswith("temp_"):
                try:
                    p.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove {p}: {e}")
        elif p.is_dir() and p.name.startswith("temp_"):
            try:
                shutil.rmtree(p)
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Could not remove {p}: {e}")

    logger.info(f"Workspace cleanup complete: Removed {deleted_count} temporary intermediate files.")


# ---------------------------------------------------------
# END-TO-END PIPELINE RUNNER
# ---------------------------------------------------------
def run_clipping_pipeline(
    input_source: str,
    output_filename: str = "viral_short.mp4",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    duration: Optional[float] = None,
    facecam_preset: str = "bottom-right",
    facecam_coords: Optional[Tuple[int, int, int, int]] = None,
    whisper_model: str = "base.en",
    workspace_dir: Optional[Path] = None
) -> Tuple[Path, Dict[str, any]]:
    """Runs the complete YouTube/Twitch to Viral 9:16 Shorts clipping pipeline."""
    work_dir = workspace_dir or Path(os.getcwd())
    output_mp4 = work_dir / output_filename
    temp_slice_mp4 = work_dir / f"temp_{output_mp4.stem}_slice.mp4"
    temp_ass = work_dir / f"temp_{output_mp4.stem}_subs.ass"

    try:
        # Step 1: Extract slice with Zero-Drift PTS reset (Rule A)
        cut_segment_with_zero_drift(
            input_source=input_source,
            output_sliced_path=temp_slice_mp4,
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )

        # Step 2: Transcribe speech with faster-whisper (Rule C)
        segments, _ = extract_audio_and_transcribe(
            video_path=temp_slice_mp4,
            whisper_model_name=whisper_model,
            temp_dir=work_dir
        )

        # Step 3: Build Hormozi Word-by-Word Subtitles ASS
        build_hormozi_ass_subtitles(
            segments=segments,
            output_ass_path=temp_ass,
            words_per_group=3,
            y_pos=620
        )

        # Step 4: Render viral 9:16 framing (Rule B)
        render_viral_short(
            input_video=temp_slice_mp4,
            output_short_path=output_mp4,
            subtitles_ass_path=temp_ass,
            facecam_preset=facecam_preset,
            facecam_coords=facecam_coords
        )

        # Step 5: Verification
        verification_report = verify_pipeline_output(output_mp4)
        logger.info(f"Verification Results: {json.dumps(verification_report, indent=2)}")

        if not verification_report["all_checks_passed"]:
            raise RuntimeError(f"Verification failed on deliverable: {verification_report}")

        return output_mp4, verification_report

    finally:
        # Step 6: Workspace Cleanup (Rule D)
        clean_workspace(work_dir, keep_files=[output_mp4])


# ---------------------------------------------------------
# SELF-CONTAINED TEST SUITE
# ---------------------------------------------------------
def generate_synthetic_test_stream(output_path: Path, duration_sec: int = 5) -> Path:
    """
    Generates a synthetic 1920x1080 30fps gameplay stream with:
      - Animated gameplay in center
      - Streamer facecam in bottom-right (1440, 720, 480, 360)
      - Spoken English audio voiceover with clear words
    """
    ffmpeg_cmd, _ = ensure_ffmpeg_in_path()
    temp_voice = output_path.parent / "temp_test_voice.wav"

    # Generate test speech using Python SAPI
    import win32com.client
    s = win32com.client.Dispatch("SAPI.SpVoice")
    fs = win32com.client.Dispatch("SAPI.SpFileStream")
    fs.Open(str(temp_voice), 3)  # SSFMCreateForWrite
    s.AudioOutputStream = fs
    s.Speak("Welcome to the stream today we are hitting insane trick shots")
    fs.Close()

    # Generate 1920x1080 test video with gameplay canvas and facecam box in bottom right
    # Gameplay canvas: testsrc
    # Facecam box: color=green:s=480x360 with dynamic drawbox/mandelbrot
    filter_graph = (
        "testsrc=duration=5:size=1920x1080:rate=30[game];"
        "mandelbrot=size=480x360:rate=30:maxiter=100[cam];"
        "[game][cam]overlay=1440:720[outv]"
    )
    cmd = [
        ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error",
        "-filter_complex", filter_graph,
        "-i", str(temp_voice),
        "-map", "[outv]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration_sec),
        str(output_path)
    ]
    subprocess.run(cmd, check=True)
    if temp_voice.exists():
        temp_voice.unlink()
    logger.info(f"Generated synthetic test stream: {output_path}")
    return output_path


def run_self_verification() -> bool:
    """Runs a complete end-to-end test verification of all 4 architectural rules."""
    work_dir = Path("e:/video")
    test_stream = work_dir / "temp_synthetic_stream.mp4"
    final_short = work_dir / "test_viral_short.mp4"

    logger.info("==================================================")
    logger.info("STARTING NATIVE PIPELINE MULTI-STAGE VERIFICATION")
    logger.info("==================================================")

    # 1. Environment check
    ffmpeg_cmd, ffprobe_cmd = ensure_ffmpeg_in_path()
    v_encoder, v_preset = check_gpu_encoder()
    logger.info(f"FFmpeg binary: {ffmpeg_cmd}")
    logger.info(f"FFprobe binary: {ffprobe_cmd}")
    logger.info(f"Active encoder: {v_encoder} ({v_preset})")

    # 2. Generate test stream
    generate_synthetic_test_stream(test_stream, duration_sec=5)

    # 3. Run Pipeline
    deliverable, report = run_clipping_pipeline(
        input_source=str(test_stream),
        output_filename="test_viral_short.mp4",
        start_time="0",
        duration=4.5,
        facecam_preset="bottom-right",
        whisper_model="base.en",
        workspace_dir=work_dir
    )

    logger.info("==================================================")
    logger.info("VERIFICATION REPORT:")
    logger.info(f" Deliverable: {deliverable}")
    logger.info(f" Resolution: {report['resolution']} (Expected: 1080x1920)")
    logger.info(f" Video Start PTS: {report['video_start_time']} (Expected: 0.000000s)")
    logger.info(f" Audio Start PTS: {report['audio_start_time']} (Expected: 0.000000s)")
    logger.info(f" Zero-Drift Synced: {report['pts_zero_drift_synced']}")
    logger.info(f" Decode Error-Free: {report['decode_error_free']}")
    logger.info("==================================================")

    # Verify Rule D: workspace contains ONLY deliverable mp4 files and stream_clipper.py
    remaining_files = [f.name for f in work_dir.iterdir()]
    logger.info(f"Files in workspace: {remaining_files}")
    for rf in remaining_files:
        if not (rf.endswith(".mp4") or rf == "stream_clipper.py"):
            logger.warning(f"Uncleaned file found in workspace: {rf}")

    return report["all_checks_passed"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Viral 9:16 Shorts Generation Pipeline")
    parser.add_argument("--url", help="YouTube/Twitch stream URL or local video path")
    parser.add_argument("--start", help="Start timestamp (seconds or HH:MM:SS)")
    parser.add_argument("--end", help="End timestamp (seconds or HH:MM:SS)")
    parser.add_argument("--duration", type=float, help="Clip duration in seconds")
    parser.add_argument("--output", default="viral_short.mp4", help="Output MP4 file name")
    parser.add_argument("--facecam-preset", default="bottom-right", choices=["bottom-right", "bottom-left", "top-right", "top-left"])
    parser.add_argument("--facecam-crop", help="Custom facecam crop as x,y,w,h")
    parser.add_argument("--whisper-model", default="base.en", help="faster-whisper model (e.g. base.en, tiny.en, small.en)")
    parser.add_argument("--test-render", action="store_true", help="Run end-to-end self-test and verification")
    parser.add_argument("--verify-only", help="Verify existing MP4 file compliance")

    args = parser.parse_args()

    if args.test_render:
        success = run_self_verification()
        sys.exit(0 if success else 1)
    elif args.verify_only:
        rep = verify_pipeline_output(Path(args.verify_only))
        print(json.dumps(rep, indent=2))
        sys.exit(0 if rep["all_checks_passed"] else 1)
    elif args.url:
        custom_crop = None
        if args.facecam_crop:
            parts = [int(p.strip()) for p in args.facecam_crop.split(",")]
            if len(parts) == 4:
                custom_crop = tuple(parts)

        run_clipping_pipeline(
            input_source=args.url,
            output_filename=args.output,
            start_time=args.start,
            end_time=args.end,
            duration=args.duration,
            facecam_preset=args.facecam_preset,
            facecam_coords=custom_crop,
            whisper_model=args.whisper_model
        )
    else:
        parser.print_help()
