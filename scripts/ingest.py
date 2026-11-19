#!/usr/bin/env python3
"""
ingest.py - Universal Video Ingestion Module
Handles local file paths and YouTube URLs via yt-dlp.
Supports cookies from /etc/secrets/cookies.txt, local cookies.txt, and YOUTUBE_COOKIES env var.
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

def find_cookie_file() -> Optional[Path]:
    """Finds cookies.txt across standard locations (Render Secret Files, local app dir, env var)."""
    candidates = [
        Path("/etc/secrets/cookies.txt"),
        Path("cookies.txt"),
        Path("/app/cookies.txt"),
        Path(__file__).resolve().parent.parent / "cookies.txt"
    ]
    for c in candidates:
        if c.exists() and c.stat().st_size > 0:
            logger.info(f"Using cookie file: {c}")
            return c

    # Check env var
    env_cookies = os.environ.get("YOUTUBE_COOKIES")
    if env_cookies and len(env_cookies.strip()) > 10:
        target = Path("/tmp/cookies.txt") if os.name != "nt" else Path("temp_work/cookies.txt")
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.write_text(env_cookies.strip(), encoding="utf-8")
            logger.info(f"Loaded cookies from YOUTUBE_COOKIES env var into {target}")
            return target
        except Exception as e:
            logger.warning(f"Could not write cookies from env var: {e}")

    return None

def ingest_video(
    source: str,
    output_path: Path,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    duration: Optional[float] = None,
    quality: Optional[str] = None,
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

    cookie_file = find_cookie_file()
    max_h = int(quality) if quality and quality.isdigit() else 2160

    # Build format selector with clean fallbacks
    format_spec = (
        f"bestvideo[height<={max_h}][ext=mp4]+bestaudio[ext=m4a]/"
        f"bestvideo[height<={max_h}]+bestaudio/"
        f"best[height<={max_h}]/"
        f"bestvideo+bestaudio/best"
    )

    # Detect JavaScript runtimes (node/deno) for yt-dlp signature challenge deciphering
    js_runtimes = {}
    if shutil.which("node") or shutil.which("nodejs") or Path("/usr/bin/node").exists():
        js_runtimes["node"] = {}
    if shutil.which("deno") or Path("/usr/local/bin/deno").exists() or Path("/root/.deno/bin/deno").exists():
        js_runtimes["deno"] = {}

    # Extraction strategies: (extractor_dict, use_cookies_bool)
    # Allows falling back to unauthenticated mobile/VR clients if the user account has SABR-only streaming enabled
    strategies = []
    if cookie_file and cookie_file.exists():
        # First try clients that support cookies without SABR enforcement
        strategies.append(({"player_client": ["ios"]}, True))
        strategies.append(({"player_client": ["mweb"]}, True))
        strategies.append((None, True))
        strategies.append(({"player_client": ["web"]}, True))

    # Fallback to unauthenticated clients WITHOUT cookies
    # When account cookies trigger YouTube's SABR-only experiment, unauthenticated Android/VR endpoints return direct video streams
    strategies.append(({"player_client": ["android"]}, False))
    strategies.append(({"player_client": ["android_vr"]}, False))
    strategies.append(({"player_client": ["ios"]}, False))
    strategies.append(({"player_client": ["tv_embedded"]}, False))
    strategies.append((None, False))

    last_error = None

    for strat, use_cookie in strategies:
        ydl_opts = {
            "format": format_spec,
            "format_sort": ["res", "fps", "ext:mp4:m4a"],
            "outtmpl": str(output_path.with_suffix(".part.%(ext)s")),
            "merge_output_format": "mp4",
            "quiet": False,
            "no_warnings": False,
            "socket_timeout": 30,
            "nocheckcertificate": True,
            "geo_bypass": True,
            "remote_components": ["ejs:github"],
        }
        if strat:
            ydl_opts["extractor_args"] = {"youtube": strat}

        if js_runtimes:
            ydl_opts["js_runtimes"] = js_runtimes

        if ffmpeg_dir:
            ydl_opts["ffmpeg_location"] = ffmpeg_dir

        if use_cookie and cookie_file and cookie_file.exists():
            ydl_opts["cookiefile"] = str(cookie_file)

        if start_time is not None and (end_time is not None or duration is not None):
            e_time = end_time if end_time is not None else (start_time + duration)
            ydl_opts["download_ranges"] = yt_dlp.utils.download_range_func([], [[start_time, e_time]])
            ydl_opts["force_keyframes_at_cuts"] = True

        for attempt in range(1, max_retries + 1):
            try:
                strat_name = strat if strat else "default"
                auth_str = "with-cookies" if (use_cookie and cookie_file) else "no-cookies"
                logger.info(f"Attempting download with strat={strat_name} [{auth_str}] (attempt {attempt}/{max_retries})...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([source])
                last_error = None
                break
            except Exception as e:
                last_error = e
                logger.warning(f"Download attempt {attempt}/{max_retries} with {strat_name} [{auth_str}] failed: {e}")
                time.sleep(1.5 * attempt)

        if last_error is None:
            break

    # Check if download succeeded via download_ranges
    if output_path.exists() and output_path.stat().st_size > 1000:
        logger.info(f"Ingestion successful: {output_path} ({output_path.stat().st_size} bytes)")
        return output_path

    # Check for .part candidates and finalize
    candidates = list(output_path.parent.glob(f"{output_path.stem}.part.*")) + list(output_path.parent.glob(f"{output_path.stem}*"))
    for cand in candidates:
        if cand != output_path and cand.stat().st_size > 1000 and cand.suffix in [".mp4", ".mkv", ".webm", ".ts"]:
            if output_path.exists():
                output_path.unlink()
            cand.rename(output_path)
            logger.info(f"Ingestion successful (from {cand.name}): {output_path} ({output_path.stat().st_size} bytes)")
            return output_path

    # FALLBACK: Direct Stream Slice via FFmpeg if yt-dlp download_ranges had issues
    logger.info("Attempting FFmpeg direct stream URL slice fallback...")
    for fallback_strat, use_c in [
        ({"player_client": ["android"]}, False),
        ({"player_client": ["android_vr"]}, False),
        ({"player_client": ["ios"]}, False),
        (None, False)
    ]:
        try:
            extract_opts = {
                "quiet": True,
                "skip_download": True,
                "nocheckcertificate": True,
                "remote_components": ["ejs:github"]
            }
            if fallback_strat:
                extract_opts["extractor_args"] = {"youtube": fallback_strat}
            if js_runtimes:
                extract_opts["js_runtimes"] = js_runtimes
            if use_c and cookie_file and cookie_file.exists():
                extract_opts["cookiefile"] = str(cookie_file)

            with yt_dlp.YoutubeDL(extract_opts) as ydl:
                meta = ydl.extract_info(source, download=False)

            formats = meta.get("formats", [])
            # Find best video and audio stream URLs
            v_url = None
            a_url = None
            combined_url = None

            for f in reversed(formats):
                if f.get("url") and f.get("vcodec") != "none" and f.get("acodec") != "none":
                    combined_url = f.get("url")
                    break

            for f in reversed(formats):
                if f.get("url") and f.get("vcodec") != "none" and f.get("acodec") == "none":
                    if not v_url and (f.get("height") or 0) <= max_h:
                        v_url = f.get("url")
                if f.get("url") and f.get("vcodec") == "none" and f.get("acodec") != "none":
                    if not a_url:
                        a_url = f.get("url")

            import subprocess
            ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"

            if combined_url:
                cmd = [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error"]
                if start_time is not None:
                    cmd.extend(["-ss", str(start_time)])
                if end_time is not None:
                    cmd.extend(["-to", str(end_time)])
                elif duration is not None:
                    cmd.extend(["-t", str(duration)])
                cmd.extend([
                    "-i", combined_url,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-c:a", "aac", "-b:a", "192k",
                    str(output_path)
                ])
                subprocess.run(cmd, check=True)
            elif v_url and a_url:
                cmd = [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error"]
                if start_time is not None:
                    cmd.extend(["-ss", str(start_time)])
                if end_time is not None:
                    cmd.extend(["-to", str(end_time)])
                elif duration is not None:
                    cmd.extend(["-t", str(duration)])
                cmd.extend([
                    "-i", v_url,
                    "-i", a_url,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-c:a", "aac", "-b:a", "192k",
                    str(output_path)
                ])
                subprocess.run(cmd, check=True)

            if output_path.exists() and output_path.stat().st_size > 1000:
                logger.info(f"FFmpeg direct stream fallback successful (with {fallback_strat}): {output_path} ({output_path.stat().st_size} bytes)")
                return output_path
        except Exception as fe:
            logger.warning(f"FFmpeg direct stream fallback attempt with {fallback_strat} failed: {fe}")

    if last_error is not None:
        raise RuntimeError(
            f"All download attempts failed for {source}: {last_error}\n"
            f"TIP: Cloud servers (Render/AWS) require YouTube cookies. Add cookies.txt via the web UI or Render Secret Files."
        )

    raise FileNotFoundError(f"Failed to find downloaded file for {source}")

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
    parser.add_argument("--input", "-i", required=True, help="Source URL or local file path")
    parser.add_argument("--output", "-o", required=True, help="Destination MP4 file path")
    parser.add_argument("--start", "-s", help="Start timestamp in seconds or HH:MM:SS")
    parser.add_argument("--end", "-e", help="End timestamp in seconds or HH:MM:SS")
    parser.add_argument("--duration", "-d", type=float, help="Duration in seconds")
    parser.add_argument("--quality", "-q", default="2160", help="Maximum video resolution height (e.g. 2160, 1080, 720)")

    args = parser.parse_args()

    s_time = parse_time(args.start)
    e_time = parse_time(args.end)

    out = ingest_video(
        source=args.input,
        output_path=Path(args.output),
        start_time=s_time,
        end_time=e_time,
        duration=args.duration,
        quality=args.quality
    )
    print(f"SUCCESS: {out}")
