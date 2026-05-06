# -*- coding: utf-8 -*-
import httpx
from openai import OpenAI
from config import AIRCHINA_API_KEY, AIRCHINA_BASE_URL, AI_HTTP_HOST_HEADER, AI_HTTP_VERIFY_SSL


def get_llm_client() -> OpenAI:
    headers = {"Host": AI_HTTP_HOST_HEADER} if AI_HTTP_HOST_HEADER else {}
    return OpenAI(
        api_key=AIRCHINA_API_KEY,
        base_url=AIRCHINA_BASE_URL,
        http_client=httpx.Client(
            verify=AI_HTTP_VERIFY_SSL,
            headers=headers,
        ),
    )
