from rest_framework import serializers

from apps.jobs.models import JobPosting


class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = ["id", "title", "description", "created_at"]
        read_only_fields = ["id", "created_at"]
