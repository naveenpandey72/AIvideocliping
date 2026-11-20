# scripts/dataset_logger.py
"""
dataset_logger.py - Autonomous Training Dataset Logger for AI Video Clipping Models
Logs every video inspection, user prompt, system prompt, and model completion both:
1. Locally in standard JSONL fine-tuning format (training_dataset.jsonl)
2. Live Google Spreadsheet (ai cliping model data set)
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("DatasetLogger")

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_FILE = BASE_DIR / "training_dataset.jsonl"
SERVICE_ACCOUNT_FILE = BASE_DIR / "service_account.json"
DEFAULT_SPREADSHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "1Bcbi86o-flI9J6uq4pg1H1tw1iCVXqu1sSZfZnBDMHU")

def get_sheet_credentials():
    """Finds service account credentials from files or environment variables."""
    try:
        from google.oauth2 import service_account
    except ImportError:
        return None

    candidates = [
        SERVICE_ACCOUNT_FILE,
        Path("service_account.json"),
        Path("/etc/secrets/service_account.json"),
    ]
    for c in candidates:
        if c.exists():
            try:
                return service_account.Credentials.from_service_account_file(
                    str(c), scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            except Exception:
                pass

    for env_var in ["GOOGLE_SERVICE_ACCOUNT_JSON", "GDRIVE_SERVICE_ACCOUNT_JSON"]:
        val = os.environ.get(env_var)
        if val:
            if os.path.isfile(val):
                try:
                    return service_account.Credentials.from_service_account_file(
                        val, scopes=['https://www.googleapis.com/auth/spreadsheets']
                    )
                except Exception:
                    pass
            try:
                info = json.loads(val)
                return service_account.Credentials.from_service_account_info(
                    info, scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            except Exception:
                pass
    return None

def log_training_sample(
    video_url: str,
    video_title: str,
    duration: float,
    model: str,
    prompt_focus: str,
    system_prompt: str,
    user_prompt: str,
    model_response_raw: str,
    moments: List[Dict[str, Any]],
    provider: str = "Ollama",
    status: str = "success"
) -> Dict[str, Any]:
    """Appends fine-tuning interaction pair to local JSONL and Google Sheet."""
    now_iso = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # 1. Structured sample object formatted for ChatML / OpenAI / Ollama fine-tuning
    entry = {
        "timestamp": now_iso,
        "video": {
            "url": video_url,
            "title": video_title,
            "duration": duration
        },
        "metadata": {
            "model": model,
            "provider": provider,
            "prompt_focus": prompt_focus,
            "status": status
        },
        # Standard OpenAI / Ollama fine-tuning message format:
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": model_response_raw or json.dumps({"moments": moments}, indent=2)}
        ],
        "extracted_moments": moments
    }

    # 2. Append to local training_dataset.jsonl
    try:
        with open(DATASET_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.info(f"Logged training sample to {DATASET_FILE}")
    except Exception as fe:
        logger.warning(f"Could not append to local dataset file: {fe}")

    # 3. Append row to Google Spreadsheet if credentials exist
    sheet_synced = False
    creds = get_sheet_credentials()
    if creds:
        try:
            from googleapiclient.discovery import build

            service = build('sheets', 'v4', credentials=creds)

            row = [
                now_iso,
                video_url,
                video_title,
                str(duration),
                model,
                prompt_focus,
                system_prompt,
                user_prompt,
                (model_response_raw or "")[:5000],  # Cell character limit safety
                json.dumps(moments, ensure_ascii=False)[:5000],
                status
            ]

            service.spreadsheets().values().append(
                spreadsheetId=DEFAULT_SPREADSHEET_ID,
                range='A:K',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]}
            ).execute()
            sheet_synced = True
            logger.info(f"Appended training row to Google Sheet {DEFAULT_SPREADSHEET_ID}")
        except Exception as se:
            logger.warning(f"Google Sheet sync notice: {se}")

    return {
        "logged_locally": True,
        "sheet_synced": sheet_synced,
        "dataset_file": str(DATASET_FILE)
    }

if __name__ == "__main__":
    print("Dataset logger ready.")
