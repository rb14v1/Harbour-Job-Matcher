import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

from apps.common.embedding_field import EmbeddingField


class Migration(migrations.Migration):
    """
    NOTE: the `embedding` field is created via the EmbeddingField() factory
    (apps/common/embedding_field.py) rather than a frozen field instance, so
    it resolves to the correct column type (pgvector VectorField on
    Postgres, JSONField on SQLite dev) at *migrate* time based on whatever
    settings.USE_SQLITE is at that moment - not at the time this migration
    file was written. This keeps `makemigrations --check --dry-run` clean
    on either backend, since the live model (apps/jobs/models.py) builds its
    field the exact same way.
    """

    initial = True

    dependencies = [
        ("common", "0001_enable_pgvector"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="JobPosting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("embedding", EmbeddingField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_postings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
