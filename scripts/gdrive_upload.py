import os
import json
import logging
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

DEFAULT_FOLDER_ID = "15sSEzMzBc6TQ_xG22EnZS6Kaae6Qu9d6"

def get_drive_service(credentials_path_or_json: str = None):
    creds_info = None
    env_creds = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON")

    if credentials_path_or_json:
        if os.path.isfile(credentials_path_or_json):
            with open(credentials_path_or_json, "r", encoding="utf-8") as f:
                creds_info = json.load(f)
        else:
            creds_info = json.loads(credentials_path_or_json)
    elif env_creds:
        if os.path.isfile(env_creds):
            with open(env_creds, "r", encoding="utf-8") as f:
                creds_info = json.load(f)
        else:
            try:
                creds_info = json.loads(env_creds)
            except Exception:
                raise ValueError("GDRIVE_SERVICE_ACCOUNT_JSON env var could not be parsed as file or JSON.")
    else:
        candidates = [
            Path("service_account.json"),
            Path(__file__).resolve().parent.parent / "service_account.json"
        ]
        for c in candidates:
            if c.exists():
                with open(c, "r", encoding="utf-8") as f:
                    creds_info = json.load(f)
                break

    if not creds_info:
        raise FileNotFoundError("No Google Drive service account credentials found. Set GDRIVE_SERVICE_ACCOUNT_JSON or place service_account.json in the project root.")

    creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def upload_file_to_drive(file_path: str, folder_id: str = None, description: str = ""):
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File to upload does not exist: {file_path}")

    target_folder_id = folder_id or os.environ.get("GDRIVE_FOLDER_ID", DEFAULT_FOLDER_ID)
    service = get_drive_service()
    
    file_metadata = {
        "name": p.name,
        "parents": [target_folder_id],
        "description": description
    }

    media = MediaFileUpload(str(p), mimetype="video/mp4", resumable=True)

    logging.info(f"Uploading {p.name} ({round(p.stat().st_size / 1e6, 2)}MB) to Google Drive folder: {target_folder_id}...")
    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            supportsAllDrives=True,
            fields="id, name, webViewLink, webContentLink"
        ).execute()

        logging.info(f"Upload complete! File ID: {file.get('id')}, Link: {file.get('webViewLink')}")
        return {
            "success": True,
            "file_id": file.get("id"),
            "name": file.get("name"),
            "link": file.get("webViewLink"),
            "download_link": file.get("webContentLink")
        }
    except Exception as e:
        logging.error(f"Google Drive upload failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_name": p.name
        }
