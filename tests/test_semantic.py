from __future__ import annotations

import pandas as pd

from algoradar.semantic import build_semantic_index, similar_problems, tag_similarity_score


def _problems() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "problem_id": "1A",
                "name": "Theatre Square",
                "rating": 1000,
                "tags": ["math", "implementation"],
                "solved_count": 80000,
            },
            {
                "problem_id": "2A",
                "name": "Winner",
                "rating": 1400,
                "tags": ["implementation", "hashing"],
                "solved_count": 22000,
            },
            {
                "problem_id": "4A",
                "name": "Watermelon",
                "rating": 800,
                "tags": ["brute force", "math"],
                "solved_count": 120000,
            },
            {
                "problem_id": "55A",
                "name": "Math Contest",
                "rating": 1600,
                "tags": ["math", "number theory"],
                "solved_count": 9000,
            },
        ]
    )


def test_tag_similarity_is_higher_for_overlapping_tags() -> None:
    matching = tag_similarity_score(["dp", "graphs"], ["dp", "greedy"])
    unrelated = tag_similarity_score(["geometry"], ["dp", "graphs"])

    assert matching > unrelated
    assert unrelated == 0.0


def test_similar_harder_uses_fast_local_fallback() -> None:
    problems = _problems()
    index = build_semantic_index(problems, prefer_transformer=False)

    assert index.method == "tfidf-fallback"
    similar = similar_problems(problems.iloc[0], problems, index, top_n=3, harder_only=True)

    assert not similar.empty
    assert (similar["rating"] >= problems.iloc[0]["rating"]).all()
    assert "1A" not in set(similar["problem_id"])
    assert "semantic_score" in similar.columns
