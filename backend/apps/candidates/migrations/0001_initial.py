import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

from apps.common.embedding_field import EmbeddingField


class Migration(migrations.Migration):
    """
    See apps/jobs/migrations/0001_initial.py for why `embedding` is created
    via the EmbeddingField() factory instead of a frozen field instance.
    """

    initial = True

    dependencies = [
        ("common", "0001_enable_pgvector"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Candidate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("resume_text", models.TextField()),
                ("embedding", EmbeddingField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="candidates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
