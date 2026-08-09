"""Timeouts for request/response operations sent to a contact."""

from app.models import Contact

# These are deliberately conservative.  A flood operation has no bounded path
# length, so it keeps the existing baseline.  A known route gets one additional
# request/response budget for every routed hop.
ROUTE_TIMEOUT_HOP_SECONDS = 5.0
ROUTE_TIMEOUT_MAX_SECONDS = 60.0


def contact_timeout_seconds(
    contact: Contact,
    *,
    flood_timeout: float,
    max_timeout: float = ROUTE_TIMEOUT_MAX_SECONDS,
) -> float:
    """Return a response timeout appropriate for the contact's effective route.

    ``path_len`` is a hop count.  A path length of zero is a known direct route
    and therefore retains the baseline timeout; flood (``-1``) is never scaled.
    Both learned direct routes and explicit route overrides are represented by
    ``effective_route`` and are handled identically here.
    """
    if contact.effective_route_source == "flood":
        return flood_timeout

    hop_count = contact.effective_route.path_len if contact.effective_route else -1
    if hop_count < 0:
        return flood_timeout

    return min(max_timeout, flood_timeout + hop_count * ROUTE_TIMEOUT_HOP_SECONDS)
