"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import time
from uuid import uuid4


def default_audit_log_path() -> str:
    """Always resolve to <repo>/outputs/… (safe when cwd is src/)."""
    repo_root = Path(__file__).resolve().parents[2]
    return str(repo_root / "outputs" / "audit_log.json")


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into ADK callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, dict] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        """Store an interaction's input and start time; return its correlation ID."""
        correlation_id = request_id or uuid4().hex
        self._open[correlation_id] = {
            "user_id": user_id,
            "input": text,
            "started_at": utc_now_iso(),
            "started_monotonic": time.monotonic(),
        }
        return correlation_id

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
    ):
        """Close an interaction record with its response and decision metadata."""
        correlation_id = request_id
        if correlation_id is None:
            correlation_id = next(
                (
                    key for key, item in reversed(list(self._open.items()))
                    if item["user_id"] == user_id
                ),
                uuid4().hex,
            )

        pending = self._open.pop(correlation_id, None)
        completed_at = utc_now_iso()
        now = time.monotonic()
        started_monotonic = (
            pending["started_monotonic"] if pending else now
        )
        self.logs.append(
            {
                "request_id": correlation_id,
                "user_id": user_id,
                "input": pending["input"] if pending else None,
                "output": text,
                "started_at": pending["started_at"] if pending else completed_at,
                "completed_at": completed_at,
                "latency_ms": round(max(0.0, now - started_monotonic) * 1000, 3),
                "blocked": bool(blocked),
                "layer": layer,
            }
        )
        return correlation_id

    def export_json(self, filepath: str | None = None):
        """Write logs to disk (JSON array) under repo-root ``outputs/`` by default."""
        path = Path(filepath or default_audit_log_path())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.logs, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
