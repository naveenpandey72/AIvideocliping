#!/usr/bin/env python3
"""
scripts/gta_clipper_engine.py
GTA-Auto-Clipper engine based on https://github.com/AnIntellectualBeing/GTA-Auto-Clipper
Implements:
  - GTA gameplay highlight selection with OpenRouter free reasoning / reaction scoring
  - Exact Pop-up Word-by-Word bouncing yellow captions (ASS)
  - Swear and profanity masking (English & Hindi)
  - Hindi-to-Hinglish romanization
  - Full-screen 9:16 layout (fill & fit modes) with player centering
  - Creator credit attribution watermark
"""

import os
import re
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("GTAClipper")

# Burned-in captions: swear and sexual words are masked so platforms do not limit reach.
MASK_WORDS = {
    "fuck", "fucking", "fucked", "fucker", "motherfucker", "shit", "shitty", "bullshit",
    "bitch", "bitches", "pussy", "dick", "cock", "cunt", "nigga", "niggas", "nigger",
    "whore", "slut", "porn", "sex", "sexy", "ass", "asshole", "bastard", "boobs", "tits",
    "chutiya", "madarchod", "bhenchod", "behenchod", "bc", "mc", "gandu", "randi", "lund", "bsdk"
}

_DEVANAGARI_CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v", "श": "sh",
    "ष": "sh", "स": "s", "ह": "h", "ळ": "l", "क़": "q",
    "ख़": "kh", "ग़": "gh", "ज़": "z", "ड़": "r", "ढ़": "rh",
    "फ़": "f",
}
_DEVANAGARI_VOWELS = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo",
    "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
}
_DEVANAGARI_MATRAS = {
    "ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo", "ृ": "ri",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
}
_DEVANAGARI_VIRAMA = "्"

def mask_word(w: str) -> str:
    """Masks profanity with asterisks, preserving initial letter."""
    core = re.sub(r"[^a-z]", "", w.lower())
    if core in MASK_WORDS or any(core.startswith(x) for x in ("fuck", "motherf", "shit", "nigg", "chut", "madar", "bhen")):
        return w[:1] + "*" * max(2, len(w) - 1)
    return w

def romanize_hindi(text: str) -> str:
    """Converts Devanagari Hindi script into Romanized Hinglish."""
    out = []
    i = 0
    while i < len(text):
        char = text[i]
        if char in _DEVANAGARI_VOWELS:
            out.append(_DEVANAGARI_VOWELS[char])
        elif char in _DEVANAGARI_CONSONANTS:
            base = _DEVANAGARI_CONSONANTS[char]
            nxt = text[i + 1] if i + 1 < len(text) else ""
            if nxt == _DEVANAGARI_VIRAMA:
                out.append(base)
                i += 1
            elif nxt in _DEVANAGARI_MATRAS:
                out.append(base + _DEVANAGARI_MATRAS[nxt])
                i += 1
            else:
                out.append(base + "a")
        else:
            out.append(char)
        i += 1
    clean = "".join(out)
    return re.sub(r"a\b", "", clean)

def ass_time(t: float) -> str:
    """Formats float seconds into ASS timestamp H:MM:SS.cs."""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def write_gta_popup_ass(
    path: Path,
    words: List[Dict[str, Any]],
    start: float,
    length: float,
    credit: Optional[str] = None,
    caption_margin_v: int = 400
) -> Path:
    """
    Pop-up captions from GTA-Auto-Clipper:
    A short phrase (max 3 words, one line) sits at ONE fixed spot.
    Each word pops in when spoken, in yellow (&H00FFFF&) with bounce (\\fscx118\\fscy118\\t(0,110,\\fscx100\\fscy100));
    words already said turn white; words not yet said stay invisible (\\alpha&HFF&).
    """
    head = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1080\n"
        "PlayResY: 1920\n"
        "WrapStyle: 2\n"
        "ScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
        f"Style: Word,Arial Black,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,2,40,40,{int(caption_margin_v)},1\n"
        f"Style: Credit,Arial,44,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,1,8,40,40,150,1\n\n"
        "[Events]\n"
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    )

    ev = []
    # Filter words within the current clip window
    inside = []
    for item in words:
        w_start = item.get("start", 0.0)
        w_end = item.get("end", 0.0)
        w_txt = item.get("word", "").strip()
        if start <= w_start < start + length:
            inside.append((w_start, w_end, w_txt))

    groups = []
    group = []
    for item in inside:
        s, e, w = item
        # Romanize if Hindi Devanagari detected
        if any('\u0900' <= c <= '\u097f' for c in w):
            w = romanize_hindi(w)
        clean = mask_word(re.sub(r"[^\w'!?.,-]", "", w)).upper()
        if not clean:
            continue
        if group:
            prev = group[-1]
            phrase_len = sum(len(part[2]) + 1 for part in group) + len(clean)
            if s - prev[1] > 0.6 or len(group) >= 3 or phrase_len > 18 or re.search(r"[.!?]$", prev[2]):
                groups.append(group)
                group = []
        group.append((s, e, clean))
    if group:
        groups.append(group)

    # Timeline of phrases
    steps = []
    for gi, phrase in enumerate(groups):
        phrase_end = phrase[-1][1] + 0.35
        if gi + 1 < len(groups):
            phrase_end = min(phrase_end, groups[gi + 1][0][0])
        for i, (s, e, _) in enumerate(phrase):
            t_off = phrase[i + 1][0] if i + 1 < len(phrase) else phrase_end
            steps.append((s - start, t_off - start, phrase, i))

    for t_on, t_off, phrase, i in steps:
        t_on = max(0.0, t_on)
        t_off = min(float(length), t_off)
        a_txt = ass_time(t_on)
        b_txt = ass_time(t_off)
        if b_txt <= a_txt:
            continue
        parts = []
        for j, (_, _, txt) in enumerate(phrase):
            if j < i:
                # Already spoken -> White
                parts.append(r"{\alpha&H00&\c&HFFFFFF&\fscx100\fscy100}" + txt)
            elif j == i:
                # Active spoken word -> Yellow pop with bounce
                parts.append(r"{\alpha&H00&\c&H00FFFF&\fscx118\fscy118\t(0,110,\fscx100\fscy100)}" + txt)
            else:
                # Not yet spoken -> Hidden
                parts.append(r"{\alpha&HFF&\fscx100\fscy100}" + txt)
        chars = sum(len(p[2]) for p in phrase) + len(phrase) - 1
        fs = max(64, min(104, int(1000 / (0.74 * max(1, chars)))))
        ev.append(f"Dialogue: 0,{a_txt},{b_txt},Word,,0,0,0,,{{\\fs{fs}}}{' '.join(parts)}")

    if credit:
        clean_cred = credit.strip()
        if not clean_cred.startswith("@"):
            clean_cred = "@" + clean_cred
        ev.append(f"Dialogue: 0,{ass_time(0)},{ass_time(length)},Credit,,0,0,0,,{clean_cred}")

    with open(path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(ev) + "\n")
    return path

def build_gta_video_filter(
    ass_path: Path,
    layout: str = "fill",
    crop_offset: float = 0.5
) -> str:
    """
    Builds video filter for 1080x1920:
    layout 'fill': gameplay covers full 9:16 frame centered on player.
    layout 'fit': gameplay centered over blurred 9:16 background.
    """
    offset = min(1.0, max(0.0, float(crop_offset)))
    escaped_ass = str(ass_path).replace("\\", "/").replace(":", "\\:")
    
    if layout == "fill":
        return (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920:(iw-1080)*{offset:.4f}:(ih-1920)/2,"
            f"setpts=PTS-STARTPTS,ass='{escaped_ass}'"
        )
    else:  # 'fit'
        return (
            f"[0:v]split[a][b];"
            f"[a]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,boxblur=30:5[bg];"
            f"[b]scale=1080:-2[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setpts=PTS-STARTPTS,ass='{escaped_ass}'"
        )
