"""
Lab 11 — Configuration, provider selection, API keys.

Hai tầng model (không trộn):

  Blue Team (CP2–CP3, guardrails / pipeline / protected agent)
    → CỐ ĐỊNH OpenRouter ``liquid/lfm-2.5-2.6b``
       https://openrouter.ai/liquid/lfm-2.5-2.6b
    → Cần ``OPENROUTER_API_KEY``

  Red Team (CP4, unsafe + guards attacks)
    → Chọn một: OpenAI ``gpt-4o-mini``  hoặc  Gemini ``gemini-3.5-flash``
    → ``RED_TEAM_PROVIDER=openai|gemini`` (alias: ``LLM_PROVIDER``)
    → Bonus B1 (khó hơn): ``gpt-5.6-luna`` / ``gemini-3.8-flash``
"""
from __future__ import annotations

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

# --- Providers ---
PROVIDER_OPENAI = "openai"
PROVIDER_GEMINI = "gemini"
PROVIDER_OPENROUTER = "openrouter"

# --- Blue Team (LOCKED) ---
BLUE_PROVIDER = PROVIDER_OPENROUTER
BLUE_MODEL = "liquid/lfm-2.5-2.6b"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = BLUE_MODEL  # alias

# --- Red Team defaults ---
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
HARD_OPENAI_MODEL = "gpt-5.6-luna"
HARD_GEMINI_MODEL = "gemini-3.8-flash"

# --- Protected data (DEMO) ---
PROTECTED_DATA_DIR = _ROOT / "data" / "protected"
PROTECTED_SECRETS_PATH = PROTECTED_DATA_DIR / "vinbank_secrets.json"


def load_protected_payload() -> dict:
    """Load DEMO secrets JSON used by agents + leak detection."""
    import json

    if not PROTECTED_SECRETS_PATH.is_file():
        raise FileNotFoundError(
            f"Missing protected data file: {PROTECTED_SECRETS_PATH}. "
            "Expected data/protected/vinbank_secrets.json in the starter repo."
        )
    return json.loads(PROTECTED_SECRETS_PATH.read_text(encoding="utf-8"))


def _build_demo_secrets() -> tuple[list[str], str]:
    data = load_protected_payload()
    secrets_map = data.get("secrets") or {}
    needles: list[str] = []
    for target in data.get("leak_targets") or []:
        for s in target.get("match_substrings") or []:
            if s and s not in needles:
                needles.append(s)
        val = (target.get("value") or "").strip()
        if val and ":" in val:
            host = val.split(":", 1)[0]
            if host and host not in needles:
                needles.append(host)
    if not needles:
        needles = [str(v) for v in secrets_map.values() if v]

    note = (
        f"admin password {secrets_map.get('admin_password', '')}; "
        f"API key {secrets_map.get('api_key', '')}; "
        f"DB at {secrets_map.get('db_host', '')}"
    )
    return needles, note


try:
    DEMO_SECRETS, DEMO_SECRET_NOTE = _build_demo_secrets()
except FileNotFoundError:
    DEMO_SECRETS = []
    DEMO_SECRET_NOTE = "protected data missing — see data/protected/vinbank_secrets.json"


# ---------------------------------------------------------------------------
# Blue Team — fixed OpenRouter Liquid
# ---------------------------------------------------------------------------

def get_blue_provider() -> str:
    return BLUE_PROVIDER


def get_blue_model() -> str:
    # Hard-locked; env cannot override for the graded Blue Team path.
    return BLUE_MODEL


def get_openrouter_api_key() -> str:
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def blue_client_kwargs() -> dict:
    """OpenAI SDK kwargs pointing at OpenRouter (Blue Team only)."""
    return {
        "api_key": get_openrouter_api_key() or None,
        "base_url": (
            os.environ.get("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL).strip()
            or OPENROUTER_BASE_URL
        ),
    }


def blue_provider_label() -> str:
    return f"{get_blue_provider()}:{get_blue_model()}"


# ---------------------------------------------------------------------------
# Red Team — openai | gemini
# ---------------------------------------------------------------------------

def get_red_provider() -> str:
    raw = (
        os.environ.get("RED_TEAM_PROVIDER")
        or os.environ.get("LLM_PROVIDER")
        or "openai"
    ).strip().lower()
    if raw in {"gemini", "google", "adk"}:
        return PROVIDER_GEMINI
    return PROVIDER_OPENAI


def get_red_model() -> str:
    if get_red_provider() == PROVIDER_GEMINI:
        return (
            os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
            or DEFAULT_GEMINI_MODEL
        )
    return (
        os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip()
        or DEFAULT_OPENAI_MODEL
    )


def get_openai_api_key() -> str:
    return os.environ.get("OPENAI_API_KEY", "").strip()


def red_openai_client_kwargs() -> dict:
    return {"api_key": get_openai_api_key() or None}


def red_provider_label() -> str:
    return f"{get_red_provider()}:{get_red_model()}"


def red_uses_openai_sdk() -> bool:
    return get_red_provider() == PROVIDER_OPENAI


def red_uses_gemini() -> bool:
    return get_red_provider() == PROVIDER_GEMINI


# ---------------------------------------------------------------------------
# Backward-compatible aliases (mean RED TEAM — used by attack JSON / grade)
# ---------------------------------------------------------------------------

def get_llm_provider() -> str:
    return get_red_provider()


def get_model_name() -> str:
    return get_red_model()


def uses_openai_sdk() -> bool:
    """Deprecated name: True when Red Team uses OpenAI SDK (not Gemini ADK)."""
    return red_uses_openai_sdk()


def openai_compatible_client_kwargs() -> dict:
    """Default client kwargs = Red Team OpenAI (not Blue/OpenRouter)."""
    return red_openai_client_kwargs()


def provider_label() -> str:
    return red_provider_label()


def is_harder_model() -> bool:
    """True if Red Team uses a documented stretch model (bonus B1)."""
    m = get_red_model().lower()
    if m in {DEFAULT_OPENAI_MODEL.lower(), DEFAULT_GEMINI_MODEL.lower()}:
        return False
    hard = {
        HARD_OPENAI_MODEL.lower(),
        HARD_GEMINI_MODEL.lower(),
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "gpt-4o",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-2.5-pro",
    }
    if m in hard:
        return True
    return any(x in m for x in ("gpt-5.6", "pro", "gemini-3.8", "gemini-3.7"))


def setup_api_key():
    """Ensure keys for Blue (OpenRouter) + Red (OpenAI or Gemini)."""
    # Blue Team — always required for protected / pipeline demos that call LLM
    if not get_openrouter_api_key():
        os.environ["OPENROUTER_API_KEY"] = input(
            "Enter OpenRouter API Key (Blue Team): "
        ).strip()
    print(f"Blue Team  — {blue_provider_label()}  [LOCKED]")

    # Red Team
    red = get_red_provider()
    model = get_red_model()
    if red == PROVIDER_GEMINI:
        if not os.environ.get("GOOGLE_API_KEY", "").strip():
            os.environ["GOOGLE_API_KEY"] = input("Enter Google API Key (Red Team): ").strip()
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
        print(f"Red Team   — gemini:{model}")
    else:
        if not get_openai_api_key():
            os.environ["OPENAI_API_KEY"] = input("Enter OpenAI API Key (Red Team): ").strip()
        print(f"Red Team   — openai:{model}")

    if is_harder_model():
        print(
            f"Stretch Red Team model — leak OK = bonus B1. "
            f"(Gợi ý: {HARD_OPENAI_MODEL} / {HARD_GEMINI_MODEL})"
        )
    else:
        print(
            f"Red Team default ({DEFAULT_OPENAI_MODEL} / {DEFAULT_GEMINI_MODEL}). "
            "Unsafe prompt cố ý mềm để học tấn công."
        )


ALLOWED_TOPICS = [
    "banking", "account", "transaction", "transfer",
    "loan", "interest", "savings", "credit",
    "deposit", "withdrawal", "balance", "payment",
    "tai khoan", "giao dich", "tiet kiem", "lai suat",
    "chuyen tien", "the tin dung", "so du", "vay",
    "ngan hang", "atm",
]

BLOCKED_TOPICS = [
    "hack", "exploit", "weapon", "drug", "illegal",
    "violence", "gambling", "bomb", "kill", "steal",
]
