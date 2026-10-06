"""Small, database-grounded property assistant (no external LLM required)."""

import re
from typing import Any

from app.modules.search.natural_language import parse_property_search
from app.modules.search.serach_repository import SearchRepository


def _text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _feature_is_documented(property_: Any, feature: str) -> bool:
    terms = SearchRepository.FEATURE_TERMS.get(feature, (feature,))
    listing_text = " ".join(
        _text(getattr(property_, field, None)).casefold()
        for field in ("title", "description", "address")
    )
    return any(term.casefold() in listing_text for term in terms)


def _family_size(question: str) -> int | None:
    patterns = (
        r"\bfamily\s+of\s+(\d+)\b",
        r"\bfamily\s+of\s+(one|two|three|four|five|six|seven|eight)\b",
        r"\b(\d+)\s+(?:people|persons|family members)\b",
    )
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}
    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            value = match.group(1).casefold()
            return words.get(value, int(value) if value.isdigit() else None)
    return None


def _score_property(property_: Any, intent: dict[str, Any], family_size: int | None) -> tuple[float, list[str], list[str]]:
    score = 0.0
    reasons: list[str] = []
    caveats: list[str] = []
    price = getattr(property_, "price", None)
    bedrooms = getattr(property_, "bedrooms", None)

    # Avoid ranking obvious placeholder/corrupt records above usable listings.
    title = _text(getattr(property_, "title", None))
    city_value = _text(getattr(property_, "city", None))
    if len(title) >= 5:
        score += 1
    else:
        score -= 2
        caveats.append("listing title is incomplete")
    if len(city_value) >= 3:
        score += 1
    else:
        score -= 3
        caveats.append("location information looks incomplete")
    try:
        bathroom_count = int(getattr(property_, "bathrooms", None))
        if 1 <= bathroom_count <= 8:
            score += 0.5
        elif bathroom_count > 8:
            score -= 2
            caveats.append(f"the recorded bathroom count ({bathroom_count}) looks unusual")
    except (TypeError, ValueError):
        pass

    requested_type = intent.get("property_type")
    actual_type = getattr(getattr(property_, "property_type", None), "value", getattr(property_, "property_type", None))
    if requested_type:
        if str(actual_type).casefold() == requested_type.casefold():
            score += 4
            reasons.append(f"it is a {str(actual_type).lower()}")
        else:
            score -= 4
            caveats.append(f"requested {requested_type.lower()}, listing is {str(actual_type).lower()}")

    place = intent.get("city")
    if place:
        stored_places = [
            _text(getattr(property_, field, None)).casefold()
            for field in ("city", "district", "address")
        ]
        if any(re.search(rf"\b{re.escape(place.casefold())}\b", value) for value in stored_places):
            score += 3
            reasons.append(f"it is in/near {place}")
        else:
            caveats.append(f"location does not match {place}")

    desired_bedrooms = intent.get("bedrooms")
    if desired_bedrooms is None and family_size:
        # Practical default: family bedrooms plus a shared living area.
        desired_bedrooms = max(1, family_size - 1)
    if desired_bedrooms is not None and bedrooms is not None:
        difference = int(bedrooms) - desired_bedrooms
        if difference >= 0:
            score += 3 + 1 / (1 + difference)
            reasons.append(f"it has {bedrooms} bedrooms" + (f" (at least {desired_bedrooms} suggested)" if family_size and not intent.get("bedrooms") else ""))
        else:
            score += max(0, 1 + difference * 0.25)
            caveats.append(f"it has {bedrooms} bedrooms; {desired_bedrooms} is the suggested minimum")

    for field, label in (("min_price", "price is within the requested range"), ("max_price", "price is within the requested range")):
        bound = intent.get(field)
        if bound is not None and price is not None:
            if (field == "min_price" and price >= bound) or (field == "max_price" and price <= bound):
                score += 2
                reasons.append(label)
            else:
                score -= 1
                caveats.append(f"price {price:,.0f} is outside the requested budget")

    try:
        numeric_price = float(price)
        if numeric_price <= 0:
            score -= 2
            caveats.append("recorded price is invalid")
        elif numeric_price < 1_000:
            score -= 1
            caveats.append("recorded price looks unusually low; confirm it with the seller")
    except (TypeError, ValueError):
        pass

    for feature in intent.get("features", []):
        if _feature_is_documented(property_, feature):
            score += 2
            reasons.append(f"listing mentions {feature}")
        else:
            caveats.append(f"{feature} is not documented in the listing")

    return score, reasons, list(dict.fromkeys(caveats))


def _format_price(value: Any) -> str:
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return "price not provided"


def answer_property_question(question: str, properties: list[Any]) -> dict[str, Any]:
    """Rank retrieved property rows and produce an answer grounded in their fields."""
    intent = parse_property_search(question)
    family_size = _family_size(question)
    ranked = []
    for property_ in properties:
        score, reasons, caveats = _score_property(property_, intent, family_size)
        ranked.append((score, property_, reasons, caveats))
    ranked.sort(key=lambda row: (-row[0], getattr(row[1], "price", float("inf")) or float("inf"), getattr(row[1], "id", 0) or 0))

    if not ranked:
        return {
            "answer": "I couldn't find any available properties in the database yet. Add available listings and ask me again.",
            "intent": {
                **intent,
                "family_size": family_size,
                "suggested_bedrooms": (
                    intent.get("bedrooms")
                    if intent.get("bedrooms") is not None
                    else max(1, family_size - 1) if family_size else None
                ),
            },
            "recommendation": None,
            "alternatives": [],
            "sources": [],
        }

    best = ranked[0]
    _, property_, reasons, caveats = best
    title = _text(getattr(property_, "title", None)) or f"Property #{property_.id}"
    location = ", ".join(filter(None, (_text(getattr(property_, "city", None)), _text(getattr(property_, "district", None)))))
    bedrooms = getattr(property_, "bedrooms", None)
    bathrooms = getattr(property_, "bathrooms", None)
    property_id = getattr(property_, "id", None)

    answer = (
        f"Based on your question, I recommend {title} (Property #{property_id}). "
        f"It costs {_format_price(getattr(property_, 'price', None))} and has "
        f"{bedrooms if bedrooms is not None else 'an unspecified number of'} bedrooms"
        f" and {bathrooms if bathrooms is not None else 'an unspecified number of'} bathrooms"
        + (f" in {location}" if location else "")
        + "."
    )
    if reasons:
        answer += " Why it fits: " + "; ".join(dict.fromkeys(reasons)) + "."
    if caveats:
        answer += " Please note: " + "; ".join(caveats) + "."
    if family_size and not intent.get("bedrooms"):
        answer += f" I assumed a {family_size}-person family would prefer at least {max(1, family_size - 1)} bedrooms; tell me if you prefer a different layout."

    def serialize(row: tuple[float, Any, list[str], list[str]]) -> dict[str, Any]:
        item = row[1]
        return {
            "id": getattr(item, "id", None),
            "title": getattr(item, "title", None),
            "price": getattr(item, "price", None),
            "city": getattr(item, "city", None),
            "district": getattr(item, "district", None),
            "property_type": getattr(getattr(item, "property_type", None), "value", getattr(item, "property_type", None)),
            "bedrooms": getattr(item, "bedrooms", None),
            "bathrooms": getattr(item, "bathrooms", None),
            "image_url": getattr(item, "image_url", None),
            "reasons": row[2],
            "caveats": row[3],
        }

    return {
        "answer": answer,
        "intent": {
            **intent,
            "family_size": family_size,
            "suggested_bedrooms": (
                intent.get("bedrooms")
                if intent.get("bedrooms") is not None
                else max(1, family_size - 1) if family_size else None
            ),
        },
        "recommendation": serialize(best),
        "alternatives": [serialize(row) for row in ranked[1:4]],
        "sources": [property_id],
    }
