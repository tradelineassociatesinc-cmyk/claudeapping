"""Thin wrapper around the Anthropic SDK: structured output, refusal fallback, cost logging."""
from __future__ import annotations

import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, TypeVar

from pydantic import BaseModel

from fra import config as C

T = TypeVar("T", bound=BaseModel)


class AIUnavailable(RuntimeError):
    pass


def available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def _client():
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover
        raise AIUnavailable("The anthropic package is not installed.") from e
    if not available():
        raise AIUnavailable("No ANTHROPIC_API_KEY is configured. Add it to the environment to enable AI reading and drafting.")
    return anthropic.Anthropic(timeout=900.0, max_retries=3)


def file_block(path: Path) -> dict:
    data = base64.standard_b64encode(path.read_bytes()).decode()
    ext = path.suffix.lower()
    if ext == ".pdf":
        return {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}}
    media = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif"}.get(ext)
    if media:
        return {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}}
    raise AIUnavailable(f"{path.suffix} files can't be read by the AI yet — upload a PDF or an image, or enter the values manually.")


def cost_usd(model: str, usage) -> float:
    pin, pout = C.AI_PRICES.get(model, (4.0, 20.0))
    inp = (getattr(usage, "input_tokens", 0) or 0) + (getattr(usage, "cache_creation_input_tokens", 0) or 0) * 1.25 \
        + (getattr(usage, "cache_read_input_tokens", 0) or 0) * 0.1
    return round(inp * pin / 1e6 + (getattr(usage, "output_tokens", 0) or 0) * pout / 1e6, 4)


def structured_call(*, system: str, content: list[dict], schema: type[T], purpose: str,
                    model: Optional[str] = None, effort: str = "medium", max_tokens: int = 64000) -> tuple[T, dict]:
    """One streamed request that returns a validated `schema` instance and a usage record."""
    import anthropic

    client = _client()
    model = model or C.AI_MODEL
    kwargs = dict(
        model=model, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": content}],
        thinking={"type": "adaptive"}, output_config={"effort": effort}, output_format=schema,
    )
    # Server-side fallback on a policy decline (Claude API only).
    if model in ("claude-opus-5-5", "claude-opus-5", "claude-fable-5-1", "claude-sonnet-5-5"):
        kwargs.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    try:
        with client.beta.messages.stream(**kwargs) as stream:
            msg = stream.get_final_message()
    except anthropic.AuthenticationError as e:
        raise AIUnavailable("The Anthropic API key was rejected.") from e
    except anthropic.RateLimitError as e:
        raise AIUnavailable("The Anthropic API rate limit was reached — try again in a minute.") from e
    except anthropic.APIConnectionError as e:
        raise AIUnavailable("Could not reach the Anthropic API.") from e
    except anthropic.APIStatusError as e:
        raise AIUnavailable(f"Anthropic API error {e.status_code}: {e.message}") from e

    usage = {"at": datetime.now().isoformat(timespec="seconds"), "purpose": purpose, "model": msg.model,
             "input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens,
             "cost_usd": cost_usd(model, msg.usage), "request_id": getattr(msg, "_request_id", None)}
    if msg.stop_reason == "refusal":
        raise AIUnavailable("The model declined to process this document. Enter the values manually.")
    if msg.stop_reason == "max_tokens":
        raise AIUnavailable("The document was too long to finish in one pass. Split the PDF and retry.")
    parsed = None
    for block in msg.content:
        if block.type == "text":
            parsed = getattr(block, "parsed_output", None)
            if parsed is None:
                parsed = schema.model_validate_json(block.text)
            break
    if parsed is None:
        raise AIUnavailable("The model returned no structured result.")
    return parsed, usage
