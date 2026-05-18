import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationML:

    @staticmethod
    def build_similarity_matrix(properties):

        # Convert DB objects to dataframe
        data = []

        for p in properties:

            combined_features = f"""
            {p.city}
            {p.property_type}
            {p.bedrooms}
            {p.bathrooms}
            {p.price}
            """

            data.append({
                "id": p.id,
                "features": combined_features
            })

        df = pd.DataFrame(data)

        # Convert text features to vectors
        vectorizer = CountVectorizer()

        feature_matrix = vectorizer.fit_transform(
            df["features"]
        )

        # Similarity matrix
        similarity = cosine_similarity(feature_matrix)

        return df, similarity