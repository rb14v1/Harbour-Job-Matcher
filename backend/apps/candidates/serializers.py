from rest_framework import serializers

from apps.candidates.models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ["id", "name", "email", "resume_text", "created_at"]
        read_only_fields = ["id", "created_at"]
