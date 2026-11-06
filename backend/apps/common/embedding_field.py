"""
Defines the embedding column differently per backend, so the exact same
model code (``embedding = EmbeddingField(...)``) works whether the app is
running against Postgres+pgvector or the dev-only SQLite override.

- Postgres (default/production path): a real ``pgvector.django.VectorField``
  of dimension ``settings.EMBEDDING_DIMENSIONS``. Requires the Postgres
  ``vector`` extension, created by the migration guard in
  apps/common/migrations/0001_enable_pgvector.py.
- SQLite (``USE_SQLITE=True``, dev-only - see config/settings/base.py):
  pgvector has no SQLite backend, so the embedding is stored as a plain
  ``JSONField`` holding a list of floats instead. ``apps/common/vector_search.py``
  branches the same way to compute cosine similarity in Python for this case.

``settings.USE_SQLITE`` is fixed for the lifetime of a process (it comes
from an env var read once at settings import time), so picking the field
type at import time here is safe and deterministic for makemigrations.
"""
from django.conf import settings
from django.db import models


def EmbeddingField(**kwargs):
    if settings.USE_SQLITE:
        return models.JSONField(null=True, blank=True, **kwargs)

    # Imported lazily so the `pgvector` package is only required when it's
    # actually needed (Postgres path); it's listed in requirements.txt
    # unconditionally, but this keeps the SQLite dev path import-light.
    from pgvector.django import VectorField

    return VectorField(dimensions=settings.EMBEDDING_DIMENSIONS, null=True, blank=True, **kwargs)
