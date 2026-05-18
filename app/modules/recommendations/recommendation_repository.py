from sqlalchemy.orm import Session

from app.modules.property.property_model import Property

from .recommendation_ml import RecommendationML


class RecommendationRepository:

    @staticmethod
    def get_recommendations(
        db: Session,
        property_id: int
    ):

        # Get all properties
        properties = db.query(Property).all()

        if not properties:
            return []

        # Build similarity matrix
        df, similarity = (
            RecommendationML.build_similarity_matrix(
                properties
            )
        )

        # Find target property index
        target_index = df[df["id"] == property_id].index

        if len(target_index) == 0:
            return []

        target_index = target_index[0]

        # Similarity scores
        similarity_scores = list(
            enumerate(similarity[target_index])
        )

        # Sort by similarity
        sorted_scores = sorted(
            similarity_scores,
            key=lambda x: x[1],
            reverse=True
        )

        # Get top recommendations
        recommended_ids = []

        for i in sorted_scores[1:11]:

            property_index = i[0]

            recommended_ids.append(
                int(df.iloc[property_index]["id"])
            )

        # Query recommended properties
        recommendations = db.query(Property).filter(
            Property.id.in_(recommended_ids)
        ).all()

        return recommendations