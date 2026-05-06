# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv(override=True)

AIRCHINA_API_KEY    = os.getenv("AIRCHINA_API_KEY", "")
AIRCHINA_BASE_URL   = os.getenv("AIRCHINA_BASE_URL", "")
AI_HTTP_HOST_HEADER = os.getenv("AI_HTTP_HOST_HEADER", "")
MODEL_CHAT          = os.getenv("MODEL_CHAT", "qwen2.5-72b")

def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}

AI_HTTP_VERIFY_SSL = _env_bool("AI_HTTP_VERIFY_SSL", True)
