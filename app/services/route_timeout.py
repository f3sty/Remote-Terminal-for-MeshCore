"""Timeouts for request/response operations sent to a contact."""

from app.models import Contact

# These are deliberately conservative.  A flood operation has no bounded path
# length, so it keeps the existing baseline.  A known route gets one
# request/response budget for every physical hop.
# A request has to reach the contact and its response has to return.  Keep a
# full ten-second allowance per physical hop so a known one-hop route does not
# collide with the old ten-second operation ceiling.
ROUTE_TIMEOUT_HOP_SECONDS = 10.0
ROUTE_TIMEOUT_MAX_SECONDS = 60.0


def contact_timeout_seconds(
    contact: Contact,
    *,
    flood_timeout: float,
    max_timeout: float = ROUTE_TIMEOUT_MAX_SECONDS,
) -> float:
    """Return a response timeout appropriate for the contact's effective route.

    ``path_len`` is the number of path repeater hops.  A path length of zero is
    still one physical radio hop, so known direct routes receive one budget.
    Flood (``-1``) is never scaled. Both learned direct routes and explicit
    route overrides are represented by ``effective_route`` and handled here.
    """
    if contact.effective_route_source == "flood":
        return flood_timeout

    hop_count = contact.effective_route.path_len if contact.effective_route else -1
    if hop_count < 0:
        return flood_timeout

    physical_hop_count = hop_count + 1
    return min(
        max_timeout,
        flood_timeout + physical_hop_count * ROUTE_TIMEOUT_HOP_SECONDS,
    )
