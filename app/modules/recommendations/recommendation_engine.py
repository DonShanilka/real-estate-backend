"""Simple, explainable content-based property recommendations."""

from math import asin, cos, isfinite, radians, sin, sqrt
from typing import Any


class RecommendationEngine:
    """Rank properties by similarity to one selected property."""

    WEIGHTS = {
        "property_type": 0.20,
        "city": 0.12,
        "district": 0.08,
        "country": 0.04,
        "bedrooms": 0.10,
        "bathrooms": 0.06,
        "price": 0.14,
        "area_size": 0.08,
        "location": 0.18,
    }

    @staticmethod
    def _value(property_: Any, name: str) -> Any:
        value = getattr(property_, name, None)
        return getattr(value, "value", value)

    @staticmethod
    def _text_similarity(first: Any, second: Any) -> float | None:
        if first is None or second is None:
            return None
        return float(str(first).strip().casefold() == str(second).strip().casefold())

    @staticmethod
    def _number_similarity(first: Any, second: Any) -> float | None:
        try:
            left, right = float(first), float(second)
        except (TypeError, ValueError):
            return None
        if not isfinite(left) or not isfinite(right):
            return None
        scale = max(abs(left), abs(right), 1.0)
        return max(0.0, 1.0 - abs(left - right) / scale)

    @staticmethod
    def _location_similarity(first: Any, second: Any) -> float | None:
        coordinates = (
            getattr(first, "latitude", None),
            getattr(first, "longitude", None),
            getattr(second, "latitude", None),
            getattr(second, "longitude", None),
        )
        try:
            lat1, lon1, lat2, lon2 = map(float, coordinates)
        except (TypeError, ValueError):
            return None

        if not all(map(isfinite, (lat1, lon1, lat2, lon2))):
            return None
        if not (-90 <= lat1 <= 90 and -90 <= lat2 <= 90):
            return None
        if not (-180 <= lon1 <= 180 and -180 <= lon2 <= 180):
            return None

        lat1, lat2 = radians(lat1), radians(lat2)
        delta_lat = lat2 - lat1
        delta_lon = radians(lon2 - lon1)
        haversine = (
            sin(delta_lat / 2) ** 2
            + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        )
        distance_km = 6371.0088 * 2 * asin(sqrt(min(1.0, haversine)))
        # Within 100 km is relevant; nearer properties receive a higher score.
        return max(0.0, 1.0 - distance_km / 100.0)

    @classmethod
    def score(cls, target: Any, candidate: Any) -> float:
        """Return a 0-100 similarity score; absent fields are not penalized."""
        similarities = {
            "property_type": cls._text_similarity(
                cls._value(target, "property_type"),
                cls._value(candidate, "property_type"),
            ),
            "city": cls._text_similarity(
                cls._value(target, "city"), cls._value(candidate, "city")
            ),
            "district": cls._text_similarity(
                cls._value(target, "district"), cls._value(candidate, "district")
            ),
            "country": cls._text_similarity(
                cls._value(target, "country"), cls._value(candidate, "country")
            ),
            "bedrooms": cls._number_similarity(
                cls._value(target, "bedrooms"), cls._value(candidate, "bedrooms")
            ),
            "bathrooms": cls._number_similarity(
                cls._value(target, "bathrooms"), cls._value(candidate, "bathrooms")
            ),
            "price": cls._number_similarity(
                cls._value(target, "price"), cls._value(candidate, "price")
            ),
            "area_size": cls._number_similarity(
                cls._value(target, "area_size"), cls._value(candidate, "area_size")
            ),
            "location": cls._location_similarity(target, candidate),
        }
        available_weight = sum(
            cls.WEIGHTS[name]
            for name, value in similarities.items()
            if value is not None
        )
        if available_weight == 0:
            return 0.0

        weighted_score = sum(
            cls.WEIGHTS[name] * value
            for name, value in similarities.items()
            if value is not None
        )
        return round(100.0 * weighted_score / available_weight, 2)

    @classmethod
    def recommend(cls, target: Any, candidates: list[Any], limit: int = 10) -> list[Any]:
        """Return the highest-scoring candidates, excluding the target itself."""
        if limit <= 0:
            return []

        ranked = []
        target_id = getattr(target, "id", None)
        for candidate in candidates:
            if getattr(candidate, "id", None) == target_id:
                continue
            ranked.append((cls.score(target, candidate), candidate))

        ranked.sort(
            key=lambda item: (
                -item[0],
                getattr(item[1], "id", None) is None,
                getattr(item[1], "id", 0) or 0,
            )
        )
        return [candidate for _, candidate in ranked[:limit]]
