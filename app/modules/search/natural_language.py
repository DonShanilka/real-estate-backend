"""Rule-based parsing for common natural-language property search requests."""

import re
from typing import Any


CITIES = {
    "colombo": "Colombo",
    "kandy": "Kandy",
    "galle": "Galle",
    "negombo": "Negombo",
    "jaffna": "Jaffna",
    "gampaha": "Gampaha",
    "kalutara": "Kalutara",
    "matara": "Matara",
    "kurunegala": "Kurunegala",
    "anuradhapura": "Anuradhapura",
    "ratnapura": "Ratnapura",
    "batticaloa": "Batticaloa",
    "trincomalee": "Trincomalee",
    "nuwara eliya": "Nuwara Eliya",
    "dehiwala": "Dehiwala",
    "mount lavinia": "Mount Lavinia",
    "maharagama": "Maharagama",
}

PROPERTY_TYPES = {
    "house": "HOUSE",
    "houses": "HOUSE",
    "home": "HOUSE",
    "homes": "HOUSE",
    "apartment": "APARTMENT",
    "apartments": "APARTMENT",
    "flat": "APARTMENT",
    "flats": "APARTMENT",
    "villa": "VILLA",
    "villas": "VILLA",
    "land": "LAND",
    "plot": "LAND",
    "plots": "LAND",
}

FEATURE_PATTERNS = {
    "parking": r"\bparking\b|\bgarage\b",
    "swimming pool": r"\bswimming pool\b|\bpool\b",
    "garden": r"\bgarden\b|\byard\b",
    "furnished": r"\bfurnished\b|\bfurniture\b",
    "balcony": r"\bbalcony\b|\bbalconies\b",
    "elevator": r"\belevator\b|\blift\b",
    "security": r"\bsecurity\b|\b24[- ]hour security\b",
    "sea view": r"\bsea view\b|\bocean view\b",
    "pet friendly": r"\bpet[- ]friendly\b|\ballows pets\b",
}


def _find_city(text: str) -> str | None:
    for name in sorted(CITIES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE):
            return CITIES[name]
    return None


def _find_property_type(text: str) -> str | None:
    for word in sorted(PROPERTY_TYPES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
            return PROPERTY_TYPES[word]
    return None


def _find_room_count(text: str, room: str) -> int | None:
    match = re.search(
        rf"\b(\d+)\s*[- ]?\s*{room}(?:\s*[- ]?\s*(?:bed)?rooms?|\s*[- ]?\s*beds?)?\b",
        text,
        re.IGNORECASE,
    )
    if match:
        return int(match.group(1))
    return None


def _find_price(text: str, relation: str) -> int | None:
    amount = r"(\d[\d,]*(?:\.\d+)?)"
    unit = r"\s*(million|mn|millions|mil|crore|crores|cr|lakh|lakhs|lac|lacs|k|thousand)?\b"
    patterns = (
        rf"\b(?:{relation})\s*(?:of\s*)?(?:rs\.?\s*|lkr\s*)?{amount}{unit}",
        rf"\b(?:{relation})\s*(?:of\s*)?(?:lkr\s*)?{amount}\s*(?:rs\.?|lkr)\b",
    )
    match = next((found for pattern in patterns if (found := re.search(pattern, text, re.IGNORECASE))), None)
    if not match:
        return None

    value = float(match.group(1).replace(",", ""))
    multiplier = {
        "million": 1_000_000,
        "millions": 1_000_000,
        "mn": 1_000_000,
        "mil": 1_000_000,
        "crore": 10_000_000,
        "crores": 10_000_000,
        "cr": 10_000_000,
        "lakh": 100_000,
        "lakhs": 100_000,
        "lac": 100_000,
        "lacs": 100_000,
        "k": 1_000,
        "thousand": 1_000,
    }.get((match.group(2) or "").lower(), 1)
    return int(value * multiplier)


def parse_property_search(text: str) -> dict[str, Any]:
    """Parse the supported search terms into structured property filters.

    This intentionally uses deterministic patterns rather than an external AI API,
    so it works offline and never sends user search text to a third party.
    """
    normalized = " ".join(text.strip().split())
    features = [
        name for name, pattern in FEATURE_PATTERNS.items()
        if re.search(pattern, normalized, re.IGNORECASE)
    ]

    return {
        "city": _find_city(normalized),
        "property_type": _find_property_type(normalized),
        "bedrooms": _find_room_count(normalized, r"bed(?:room)?s?"),
        "bathrooms": _find_room_count(normalized, r"bath(?:room)?s?"),
        "min_price": _find_price(normalized, r"(?:over|above|at least|more than)"),
        "max_price": _find_price(normalized, r"(?:under|below|up to|at most|less than|max(?:imum)?)"),
        "features": features,
    }
