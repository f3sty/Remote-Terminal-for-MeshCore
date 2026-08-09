from app.models import Contact
from app.services.route_timeout import contact_timeout_seconds


KEY = "aa" * 32


def test_flood_keeps_baseline_timeout():
    contact = Contact(public_key=KEY)

    assert contact_timeout_seconds(contact, flood_timeout=5.0) == 5.0


def test_known_direct_route_adds_one_budget_per_hop():
    contact = Contact(
        public_key=KEY,
        direct_path="aabb",
        direct_path_len=2,
        direct_path_hash_mode=0,
    )

    assert contact_timeout_seconds(contact, flood_timeout=5.0) == 15.0


def test_route_override_is_scaled_and_bounded():
    contact = Contact(
        public_key=KEY,
        route_override_path="aabbcc",
        route_override_len=3,
        route_override_hash_mode=0,
    )

    assert contact_timeout_seconds(contact, flood_timeout=10.0, max_timeout=20.0) == 20.0
