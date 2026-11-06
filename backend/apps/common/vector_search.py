"""
Backend-agnostic top-k cosine similarity search over a queryset.

Same signature on both backends:

    similarity_search(queryset, query_vector, top_k, field_name="embedding")
        -> list[tuple[model_instance, float]]   # (object, cosine_similarity), best first

- Postgres: delegates to pgvector's ``CosineDistance`` so the ranking and
  top-k slicing happen in the database.
- SQLite (dev-only, ``USE_SQLITE=True``): pgvector isn't available, so
  candidates are pulled into Python and ranked there with a plain cosine
  similarity implementation. Fine for small dev/demo datasets; not meant to
  scale - that's the whole point of pgvector on the Postgres path.
"""
import math

from django.conf import settings


def _cosine_similarity(a, b):
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def similarity_search(queryset, query_vector, top_k, field_name="embedding"):
    if settings.USE_SQLITE:
        scored = []
        for obj in queryset:
            vector = getattr(obj, field_name)
            scored.append((obj, _cosine_similarity(vector, query_vector)))
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]

    from pgvector.django import CosineDistance

    annotated = queryset.annotate(
        _distance=CosineDistance(field_name, query_vector)
    ).order_by("_distance")[:top_k]
    return [(obj, 1 - obj._distance) for obj in annotated]
