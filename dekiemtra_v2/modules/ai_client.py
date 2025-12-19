# -*- coding: utf-8 -*-
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import streamlit as st

DEFAULT_GEN_CONFIG: Dict[str, Any] = {
    "temperature": 0.4,
    "top_p": 0.9,
    "max_output_tokens": 2048,
}

MAX_PROMPT_CHARS = 20_000


def _truncate(s: str, max_chars: int) -> str:
    s = s or ""
    return s if len(s) <= max_chars else s[:max_chars] + "\n\n[...ĐÃ CẮT BỚT DO QUÁ DÀI...]"


def _backoff(attempt: int) -> None:
    base = min(8.0, 2.0 ** attempt)
    time.sleep(base + random.random() * 0.6)


@dataclass
class GenResult:
    text: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None


class GeminiClient:
    """
    Wrapper cho google-generativeai:
    - Cache danh sách model theo session (tránh list_models liên tục)
    - Rotate model + retry nhẹ khi lỗi tạm thời
    - Cắt prompt nếu quá dài để giảm InvalidArgument
    """

    def __init__(self, api_key: str):
        self.api_key = (api_key or "").strip()
        self._configured = False

    def ready(self) -> bool:
        return bool(self.api_key)

    def _ensure_configured(self) -> None:
        if not self.api_key:
            return
        if st.session_state.get("_genai_api_key") == self.api_key and self._configured:
            return
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        st.session_state["_genai_api_key"] = self.api_key
        st.session_state.pop("_genai_model_priority", None)
        self._configured = True

    def _model_priority(self) -> List[str]:
        self._ensure_configured()
        if not self.api_key:
            return []

        if "_genai_model_priority" in st.session_state:
            return st.session_state["_genai_model_priority"]

        import google.generativeai as genai

        all_models = list(genai.list_models())
        valid = [
            m.name
            for m in all_models
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]

        priority: List[str] = []
        for m in valid:
            ml = m.lower()
            if "1.5" in ml and "flash" in ml:
                priority.append(m)
        for m in valid:
            ml = m.lower()
            if "1.5" in ml and "pro" in ml and m not in priority:
                priority.append(m)
        for m in valid:
            if m not in priority:
                priority.append(m)

        st.session_state["_genai_model_priority"] = priority
        return priority

    def generate(self, prompt: str, gen_config: Optional[Dict[str, Any]] = None) -> GenResult:
        if not self.api_key:
            return GenResult(error="Chưa có GOOGLE_API_KEY. Nhập ở Sidebar hoặc đặt trong st.secrets.")
        prompt = (prompt or "").strip()
        if not prompt:
            return GenResult(error="Prompt rỗng.")
        if len(prompt) > MAX_PROMPT_CHARS:
            prompt = _truncate(prompt, MAX_PROMPT_CHARS)

        self._ensure_configured()
        models = self._model_priority()
        if not models:
            return GenResult(error="Không tìm thấy model generateContent khả dụng.")

        last_err: Optional[str] = None
        import google.generativeai as genai

        for model_name in models:
            for attempt in range(2):
                try:
                    model = genai.GenerativeModel(model_name)
                    resp = model.generate_content(prompt, generation_config=(gen_config or DEFAULT_GEN_CONFIG))
                    text = getattr(resp, "text", None) or ""
                    if not text.strip():
                        raise RuntimeError("Model trả về rỗng.")
                    return GenResult(text=text, model=model_name)
                except Exception as e:
                    last_err = str(e)
                    low = last_err.lower()
                    if any(k in low for k in ["429", "rate", "resource_exhausted", "temporarily", "unavailable"]):
                        _backoff(attempt)
                        continue
                    break

        return GenResult(error=f"Hết model khả dụng. Lỗi cuối: {last_err}")
