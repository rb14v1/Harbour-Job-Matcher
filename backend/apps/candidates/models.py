from django.conf import settings
from django.db import models

from apps.common.ai import get_embedding
from apps.common.embedding_field import EmbeddingField


class Candidate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidates")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    resume_text = models.TextField()
    # Embedding of resume_text - recomputed on every save() (create or
    # update) so it always reflects the current resume_text.
    embedding = EmbeddingField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.embedding = get_embedding(self.resume_text)
        super().save(*args, **kwargs)
