from rest_framework import permissions, viewsets

from apps.candidates.models import Candidate
from apps.candidates.serializers import CandidateSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Scoped to request.user: a user can never see, update or delete
        # another user's candidates, even by guessing an object id.
        return Candidate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
