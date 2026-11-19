#!/usr/bin/env python3
"""
transcribe.py - Audio Extraction & Faster-Whisper Transcription Module
Runs faster-whisper with word_timestamps=True.
Supports CUDA/GPU auto-detection with fallback to CPU int8 compute type.
Outputs structured JSON with segment and word-level start/end timestamps.
"""

import os
import sys
import json
import shutil
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Transcribe")

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

def detect_device_and_compute():
    """Detects CUDA availability or falls back to CPU int8."""
    try:
        import ctranslate2
        cuda_types = ctranslate2.get_supported_compute_types("cuda")
        if cuda_types:
            compute_type = "float16" if "float16" in cuda_types else "int8"
            logger.info(f"CTranslate2 CUDA acceleration active ({compute_type}).")
            return "cuda", compute_type
    except Exception:
        pass
    logger.info("Using CPU execution with int8 quantization.")
    return "cpu", "int8"

def extract_audio(video_path: Path, audio_wav_path: Path) -> Path:
    """Extracts 16kHz mono PCM WAV from input media."""
    ffmpeg_cmd = ensure_ffmpeg()
    cmd = [
        ffmpeg_cmd, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(audio_wav_path)
    ]
    subprocess.run(cmd, check=True)
    return audio_wav_path

def transcribe_media(
    input_media: Path,
    output_json: Path,
    model_name: str = "base",
    language: Optional[str] = None
) -> Dict[str, Any]:
    """Transcribes media and saves structured segment and word timestamps to JSON."""
    input_path = Path(input_media).resolve()
    output_json = Path(output_json).resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)

    temp_wav = output_json.parent / f"temp_{input_path.stem}.wav"
    try:
        logger.info(f"Extracting audio from {input_path}...")
        extract_audio(input_path, temp_wav)

        device, compute_type = detect_device_and_compute()
        from faster_whisper import WhisperModel
        logger.info(f"Loading faster-whisper model '{model_name}' ({device}, {compute_type})...")
        model = WhisperModel(model_name, device=device, compute_type=compute_type)

        transcribe_kwargs = {
            "word_timestamps": True,
            "vad_filter": True
        }
        if language:
            transcribe_kwargs["language"] = language

        logger.info("Running transcription with word-level alignment...")
        segments_gen, info = model.transcribe(str(temp_wav), **transcribe_kwargs)

        results = {
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "segments": []
        }

        total_words = 0
        for s in segments_gen:
            words_data = []
            if s.words:
                for w in s.words:
                    words_data.append({
                        "word": w.word.strip(),
                        "start": round(w.start, 3),
                        "end": round(w.end, 3),
                        "probability": round(w.probability, 3)
                    })
                    total_words += 1

            results["segments"].append({
                "id": s.id,
                "start": round(s.start, 3),
                "end": round(s.end, 3),
                "text": s.text.strip(),
                "words": words_data
            })

        logger.info(f"Transcription complete: {len(results['segments'])} segments, {total_words} words. Language: {info.language}")

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return results

    finally:
        if temp_wav.exists():
            try:
                temp_wav.unlink()
            except Exception:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio/video with faster-whisper")
    parser.add_argument("--input", "-i", required=True, help="Input media file")
    parser.add_argument("--output", "-o", default="./temp_work/transcript.json", help="Output JSON path")
    parser.add_argument("--model", default="base", help="Whisper model (tiny, base, small, medium)")
    parser.add_argument("--language", help="Optional language code (e.g. en, hi)")
    args = parser.parse_args()

    data = transcribe_media(
        input_media=Path(args.input),
        output_json=Path(args.output),
        model_name=args.model,
        language=args.language
    )
    print(f"SUCCESS: Transcribed {len(data['segments'])} segments to {args.output}")
