"""Context-local outcome tracking for interactive HIKARI operations."""
from __future__ import annotations

from contextvars import ContextVar

from .ui import error as _ui_error, success as _ui_success, warning as _ui_warning

_ACTIVE_ACTION_RESULT: ContextVar[dict[str, str] | None] = ContextVar("hikari_active_action_result", default=None)


def set_action_outcome(status: str, detail: str) -> None:
    """Update the current dashboard action result, if one is being tracked."""
    result = _ACTIVE_ACTION_RESULT.get()
    if result is not None:
        result["status"] = status
        result["detail"] = " ".join(str(detail).split())[:180]


def warning_outcome(message: str) -> tuple[str, str] | None:
    """Classify terminal warning text only when it clearly signals a final outcome."""
    text = " ".join(message.lower().split())
    if "cancel" in text:
        return ("CANCELLED", message)
    if any(token in text for token in ("failed", "failure", "could not", "unable to", "error:", "unknown choice", "unknown operation", "invalid selection", "invalid choice")):
        return ("FAILED", message)
    if any(token in text for token in ("requires a git repository", "requires git", "requires an origin", "no origin is configured", "unavailable", "refusing to", "already exists", "invalid remote", "not in the listed", "no commit available", "no commits available", "nothing to release", "does not exist in", "publication skipped")):
        return ("BLOCKED", message)
    if "unknown choice" in text or "unknown operation" in text or "invalid selection" in text:
        return ("FAILED", message)
    return None


def success(message: str) -> None:
    _ui_success(message)
    current = _ACTIVE_ACTION_RESULT.get()
    if current is not None:
        prior = current.get("detail", "")
        set_action_outcome("SUCCESS", message)
        if prior and prior != "Action flow started" and "completed; see operation output" not in prior.lower() and prior != message:
            current["detail"] = (message + "; note: " + prior)[:180]


def warning(message: str) -> None:
    _ui_warning(message)
    result = _ACTIVE_ACTION_RESULT.get()
    if result is None:
        return
    classified = warning_outcome(message)
    if classified is None:
        if result.get("status") == "SUCCESS" and result.get("detail", "").startswith("Completed; see operation output"):
            set_action_outcome("SUCCESS", message)
        return
    status, detail = classified
    previous_status = result.get("status", "SUCCESS")
    previous_detail = result.get("detail", "")
    if previous_status == "SUCCESS" and previous_detail and not previous_detail.startswith("Completed; see operation output"):
        if status == "BLOCKED":
            set_action_outcome("SUCCESS", f"{previous_detail}; skipped: {detail}")
            return
        if status == "FAILED":
            detail = f"Partial: {previous_detail}; follow-up failed: {detail}"
    set_action_outcome(status, detail)


def error(message: str) -> None:
    _ui_error(message)
    set_action_outcome("FAILED", message)
