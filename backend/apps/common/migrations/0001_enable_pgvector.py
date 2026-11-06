"""
Migration guard: creates the Postgres `vector` extension (pgvector) before
any app migration defines a VectorField column. This is a no-op on SQLite
(dev-only override, USE_SQLITE=True) - see apps/common/embedding_field.py,
which uses a plain JSONField instead of VectorField in that case, so no
extension is needed there at all.

apps/jobs and apps/candidates both depend on this migration so the
extension always exists before their initial migrations run.
"""
from django.db import migrations


def enable_pgvector_extension(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    # else: SQLite dev path - embeddings are stored as JSONField, no
    # extension required or possible.


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.RunPython(enable_pgvector_extension, noop_reverse),
    ]
