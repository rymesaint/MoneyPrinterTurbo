import os
import glob
import uuid
import io
from fastapi import Request, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, List

from app.config import config
from app.utils import utils
from app.services import voice
from app.controllers.v1.base import new_router

router = new_router()

class ConfigUpdateRequest(BaseModel):
    app: Dict[str, Any]
    azure: Dict[str, Any]
    siliconflow: Dict[str, Any]
    elevenlabs: Dict[str, Any]
    ui: Dict[str, Any]
    discord: Dict[str, Any]
    youtube: Dict[str, Any]
    facebook: Dict[str, Any]

@router.get("/config", summary="Retrieve all configuration options")
def get_config():
    return utils.get_response(200, {
        "app": config.app,
        "azure": config.azure,
        "siliconflow": config.siliconflow,
        "elevenlabs": config.elevenlabs,
        "ui": config.ui,
        "discord": config.discord,
        "youtube": config.youtube,
        "facebook": config.facebook
    })

@router.post("/config", summary="Update system configuration")
def update_config(body: ConfigUpdateRequest):
    config.app.update(body.app)
    config.azure.update(body.azure)
    config.siliconflow.update(body.siliconflow)
    config.elevenlabs.update(body.elevenlabs)
    config.ui.update(body.ui)
    config.discord.update(body.discord)
    config.youtube.update(body.youtube)
    config.facebook.update(body.facebook)
    config.save_config()
    return utils.get_response(200, message="Config saved successfully")

@router.get("/fonts", summary="Retrieve all available fonts")
def get_fonts():
    font_dir = utils.font_dir()
    fonts = []
    for root, dirs, files in os.walk(font_dir):
        for file in files:
            if file.endswith(".ttf") or file.endswith(".ttc"):
                fonts.append(file)
    fonts.sort()
    return utils.get_response(200, fonts)

@router.get("/voices", summary="Retrieve available TTS voices based on provider")
def get_voices(tts_server: str = "azure-tts-v1"):
    filtered_voices = []
    if tts_server == voice.NO_VOICE_NAME:
        filtered_voices = [voice.NO_VOICE_NAME]
    elif tts_server == "siliconflow":
        filtered_voices = voice.get_siliconflow_voices()
    elif tts_server == "gemini-tts":
        filtered_voices = voice.get_gemini_voices()
    elif tts_server == "mimo-tts":
        filtered_voices = voice.get_mimo_voices()
    elif tts_server == "elevenlabs":
        filtered_voices = voice.get_elevenlabs_voices()
    else:
        # Default Azure
        all_voices = voice.get_all_azure_voices(filter_locals=None)
        for v in all_voices:
            if tts_server == "azure-tts-v2":
                if "V2" in v:
                    filtered_voices.append(v)
            else:
                if "V2" not in v:
                    filtered_voices.append(v)
    
    # Map to friendly names
    result = []
    for v in filtered_voices:
        if tts_server == "elevenlabs":
            parts = v.split(":")
            if len(parts) >= 3:
                name_gender = parts[2]
                friendly = name_gender.replace("-", " (") + ")"
            else:
                friendly = v
        else:
            friendly = v.replace("Female", "Female").replace("Male", "Male").replace("Neural", "")
        result.append({
            "id": v,
            "name": friendly
        })
    return utils.get_response(200, result)

class VoicePreviewRequest(BaseModel):
    text: str
    voice_name: str
    voice_rate: float = 1.0
    voice_volume: float = 1.0

@router.post("/voice/preview", summary="Generate a quick TTS preview audio clip")
def preview_voice(body: VoicePreviewRequest):
    temp_dir = utils.storage_dir("temp", create=True)
    audio_file = os.path.join(temp_dir, f"tmp-voice-{str(uuid.uuid4())}.mp3")
    sub_maker = voice.tts(
        text=body.text,
        voice_name=body.voice_name,
        voice_rate=body.voice_rate,
        voice_file=audio_file,
        voice_volume=body.voice_volume,
    )
    if not sub_maker or not os.path.exists(audio_file):
        raise HTTPException(status_code=500, detail="Voice synthesis failed")
    
    with open(audio_file, "rb") as f:
        data = f.read()
    try:
        os.remove(audio_file)
    except Exception:
        pass
    
    return StreamingResponse(io.BytesIO(data), media_type="audio/mp3")

@router.post("/upload", summary="Upload a temporary asset file")
def upload_file(file: UploadFile = File(...)):
    temp_dir = utils.storage_dir("temp", create=True)
    ext = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4()}{ext}"
    save_path = os.path.join(temp_dir, filename)
    with open(save_path, "wb") as f:
        f.write(file.file.read())
    return utils.get_response(200, {"file_path": save_path, "filename": file.filename})
