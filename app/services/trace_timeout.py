"""Timeout policy shared by the direct and multi-hop trace endpoints."""

TRACE_DEFAULT_TIMEOUT_SECONDS = 15.0
TRACE_TIMEOUT_MIN_SECONDS = 5.0
TRACE_TIMEOUT_MAX_SECONDS = 120.0
TRACE_TIMEOUT_MARGIN = 1.2


def trace_timeout_seconds(send_result: object) -> float:
    """Return a bounded wait based on the radio's estimated round-trip time."""
    payload = getattr(send_result, "payload", None) or {}
    suggested_timeout = payload.get("suggested_timeout")
    try:
        if suggested_timeout is None:
            raise TypeError
        timeout_seconds = float(suggested_timeout) / 1000.0 * TRACE_TIMEOUT_MARGIN
    except (TypeError, ValueError):
        timeout_seconds = TRACE_DEFAULT_TIMEOUT_SECONDS
    return max(TRACE_TIMEOUT_MIN_SECONDS, min(TRACE_TIMEOUT_MAX_SECONDS, timeout_seconds))
