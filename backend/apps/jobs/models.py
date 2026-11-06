from django.conf import settings
from django.db import models

from apps.common.ai import get_embedding
from apps.common.embedding_field import EmbeddingField


class JobPosting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_postings")
    title = models.CharField(max_length=255)
    description = models.TextField()
    # Embedding of f"{title}\n{description}" - recomputed on every save()
    # (create or update) so it always reflects the current title/description.
    embedding = EmbeddingField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.embedding = get_embedding(f"{self.title}\n{self.description}")
        super().save(*args, **kwargs)
