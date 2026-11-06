from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.candidates.models import Candidate
from apps.common.ai import generate_answer, is_stub_mode
from apps.common.vector_search import similarity_search
from apps.jobs.models import JobPosting
from apps.jobs.serializers import JobPostingSerializer


class JobPostingViewSet(viewsets.ModelViewSet):
    serializer_class = JobPostingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Scoped to request.user: a user can never retrieve, update, delete
        # or match against another user's job postings, even by guessing an
        # object id (get_object() 404s instead of leaking existence).
        return JobPosting.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def matches(self, request, pk=None):
        """GET /api/jobs/{id}/matches/?k=5

        Ranks the requesting user's own candidates against this job's
        embedding and returns the top-k, plus a generated fit-explanation
        for the single best match.
        """
        job = self.get_object()

        try:
            k = int(request.query_params.get("k", 5))
        except (TypeError, ValueError):
            k = 5
        k = max(1, min(k, 50))

        # Scoped to request.user - never matches against another user's
        # candidates, even for a job the requesting user legitimately owns.
        candidates_qs = Candidate.objects.filter(user=request.user)
        ranked = similarity_search(candidates_qs, job.embedding, top_k=k)

        matches = [
            {"candidate_id": candidate.id, "name": candidate.name, "score": round(score, 6)}
            for candidate, score in ranked
        ]

        top_match_explanation = ""
        if ranked:
            best_candidate, _ = ranked[0]
            top_match_explanation = generate_answer(job.title, [best_candidate.resume_text])

        return Response({
            "matches": matches,
            "top_match_explanation": top_match_explanation,
            "stub_mode": is_stub_mode(),
        })
