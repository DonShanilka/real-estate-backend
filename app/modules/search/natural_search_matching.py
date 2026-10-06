"""Best-effort ranking of a parsed natural search against real listings."""

import re
from typing import Any

from .serach_repository import SearchRepository

def _normalized(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def _matches_place(property_: Any, requested_place: str) -> bool:
    requested = _normalized(requested_place)
    return any(
        re.search(
            rf"\b{re.escape(requested)}\b",
            _normalized(getattr(property_, field, None)),
        )
        for field in ("city", "district", "address")
    )


def _matches_feature(property_: Any, feature: str) -> bool:
    terms = SearchRepository.FEATURE_TERMS.get(feature, (feature,))
    listing_text = " ".join(
        _normalized(getattr(property_, field, None))
        for field in ("title", "description", "address")
    )
    return any(_normalized(term) in listing_text for term in terms)


def _score(property_: Any, filters: dict[str, Any], verifiable_features: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    matched = []

    city = filters.get("city")
    district = filters.get("district")
    requested_places = [place for place in (city, district) if place]
    if requested_places:
        if any(_matches_place(property_, place) for place in requested_places):
            score += 4
            matched.append("location")

    property_type = filters.get("property_type")
    if property_type:
        actual_type = getattr(getattr(property_, "property_type", None), "value", getattr(property_, "property_type", None))
        if _normalized(actual_type) == _normalized(property_type):
            score += 3
            matched.append("property_type")

    for field in ("bedrooms", "bathrooms"):
        requested = filters.get(field)
        actual = getattr(property_, field, None)
        if requested is not None and actual is not None:
            try:
                actual_count = int(actual)
                requested_count = int(requested)
            except (TypeError, ValueError):
                continue
            if actual_count >= requested_count:
                # Prefer exact room counts, but still include listings with more rooms.
                score += 2 + 1 / (1 + actual_count - requested_count)
                matched.append(field)
            else:
                # Keep a smaller-room listing as a lower-ranked alternative
                # rather than dropping every useful database result.
                score += 1 / (1 + requested_count - actual_count)

    price = getattr(property_, "price", None)
    if price is not None:
        try:
            price = float(price)
            meets_min = filters.get("min_price") is None or price >= filters["min_price"]
            meets_max = filters.get("max_price") is None or price <= filters["max_price"]
            if meets_min and meets_max and (filters.get("min_price") is not None or filters.get("max_price") is not None):
                if filters.get("min_price") is not None:
                    matched.append("min_price")
                if filters.get("max_price") is not None:
                    matched.append("max_price")
                score += 1.5
            elif filters.get("max_price") is not None and price > filters["max_price"]:
                score += 1 / (1 + (price - filters["max_price"]) / max(filters["max_price"], 1))
            elif filters.get("min_price") is not None and price < filters["min_price"]:
                score += 1 / (1 + (filters["min_price"] - price) / max(filters["min_price"], 1))
        except (TypeError, ValueError):
            pass

    for feature in verifiable_features:
        if _matches_feature(property_, feature):
            score += 1
            matched.append(feature)

    return score, matched


def rank_database_properties(properties: list[Any], filters: dict[str, Any], limit: int = 10) -> dict[str, Any]:
    """Return best-scoring DB rows and explain criteria that could not be met."""
    requested_features = filters.get("features", [])
    verifiable_features = [
        feature for feature in requested_features
        if any(_matches_feature(property_, feature) for property_ in properties)
    ]
    unverified_features = [
        feature for feature in requested_features
        if feature not in verifiable_features
    ]

    requested_type = _normalized(filters.get("property_type"))
    ranked = []
    for property_ in properties:
        actual_type = getattr(
            getattr(property_, "property_type", None),
            "value",
            getattr(property_, "property_type", None),
        )
        # A stated property category is a hard requirement: don't recommend a
        # villa or land listing for a house search just to fill the results.
        if requested_type and _normalized(actual_type) != requested_type:
            continue
        ranked.append((_score(property_, filters, verifiable_features), property_))
    ranked.sort(
        key=lambda item: (
            -item[0][0],
            getattr(item[1], "price", float("inf")) or float("inf"),
            getattr(item[1], "id", 0) or 0,
        )
    )

    if not ranked or ranked[0][0][0] <= 0:
        return {
            "properties": [],
            "matched_filters": [],
            "relaxed_filters": [key for key, value in filters.items() if value is not None and value != []],
            "unverified_features": unverified_features,
        }

    top = ranked[:limit]
    matched = list(dict.fromkeys(name for details, _ in top for name in details[1]))
    requested = [key for key, value in filters.items() if value is not None and value != []]
    if filters.get("city") or filters.get("district"):
        requested = [key for key in requested if key not in ("city", "district")]
        requested.append("location")
    relaxed = [key for key in requested if key not in matched and key != "features"]
    if requested_features and not any(feature in matched for feature in requested_features):
        relaxed.append("features")

    return {
        "properties": [property_ for _, property_ in top],
        "matched_filters": matched,
        "relaxed_filters": relaxed,
        "unverified_features": unverified_features,
    }