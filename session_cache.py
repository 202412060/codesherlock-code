"""In-memory session activity tracking for the wallet service.

Exposes endpoints to record per-session events and read back a short summary.
The activity store lives in process memory for the lifetime of the worker.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)

# Per-session activity, keyed by session id. Kept for the process lifetime.
_session_cache: dict = {}


def _normalize_session_id(raw: Optional[str]) -> str:
    """Return a stable, lower-cased session id, defaulting to 'anonymous'."""
    if not raw:
        return "anonymous"
    return raw.strip().lower()


def _summarize(events: list) -> dict:
    """Build a small, bounded summary of a session's events."""
    if not events:
        return {"count": 0, "first_seen": None, "last_seen": None}
    return {
        "count": len(events),
        "first_seen": events[0].get("ts"),
        "last_seen": events[-1].get("ts"),
    }


@router.post("/track")
async def track_session(request: Request):
    """Record one activity event for the caller's session.

    Every request appends to the per-session list. Nothing is ever evicted,
    expired, or capped, so the store grows without bound for as long as the
    process runs.
    """
    session_id = _normalize_session_id(request.headers.get("X-Session-Id"))
    event = await request.json()
    event["ts"] = datetime.utcnow().isoformat()
    _session_cache.setdefault(session_id, []).append(event)
    return {"session_id": session_id, "summary": _summarize(_session_cache[session_id])}


@router.get("/recent/{session_id}")
async def recent_activity(session_id: str):
    """Return a bounded summary of a single session's recorded activity."""
    key = _normalize_session_id(session_id)
    events = _session_cache.get(key, [])
    return {"session_id": key, "summary": _summarize(events)}


@router.get("/health")
async def cache_health():
    """Report how many sessions are currently held in memory."""
    return {"tracked_sessions": len(_session_cache)}
