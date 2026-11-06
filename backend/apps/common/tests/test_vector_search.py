from django.test import TestCase

from apps.common.test_utils import create_user, pad_vector
from apps.common.vector_search import similarity_search
from apps.candidates.models import Candidate


class SimilaritySearchRankingTests(TestCase):
    """
    Exercises similarity_search() with hand-crafted vectors so the expected
    ranking is known ahead of time. Candidate.save() normally recomputes the
    embedding from resume_text via get_embedding(); the controlled test
    vectors below are written after creation with .update(), which bypasses
    that save() override so the stored embedding is exactly what the test
    expects.
    """

    def setUp(self):
        self.user = create_user(email="search@example.com")

        self.exact_match = Candidate.objects.create(
            user=self.user, name="Exact Match", email="exact@example.com", resume_text="placeholder"
        )
        self.close_match = Candidate.objects.create(
            user=self.user, name="Close Match", email="close@example.com", resume_text="placeholder"
        )
        self.orthogonal = Candidate.objects.create(
            user=self.user, name="Orthogonal", email="orthogonal@example.com", resume_text="placeholder"
        )
        self.opposite = Candidate.objects.create(
            user=self.user, name="Opposite", email="opposite@example.com", resume_text="placeholder"
        )

        Candidate.objects.filter(pk=self.exact_match.pk).update(embedding=pad_vector([1.0, 0.0, 0.0]))
        Candidate.objects.filter(pk=self.close_match.pk).update(embedding=pad_vector([0.9, 0.1, 0.0]))
        Candidate.objects.filter(pk=self.orthogonal.pk).update(embedding=pad_vector([0.0, 1.0, 0.0]))
        Candidate.objects.filter(pk=self.opposite.pk).update(embedding=pad_vector([-1.0, 0.0, 0.0]))

    def test_nearest_first_ordering(self):
        query_vector = pad_vector([1.0, 0.0, 0.0])
        queryset = Candidate.objects.filter(user=self.user)

        ranked = similarity_search(queryset, query_vector, top_k=4)
        ranked_ids = [obj.id for obj, _score in ranked]

        self.assertEqual(
            ranked_ids,
            [self.exact_match.id, self.close_match.id, self.orthogonal.id, self.opposite.id],
        )

    def test_exact_match_has_similarity_one(self):
        query_vector = pad_vector([1.0, 0.0, 0.0])
        queryset = Candidate.objects.filter(user=self.user)

        ranked = similarity_search(queryset, query_vector, top_k=1)
        obj, score = ranked[0]

        self.assertEqual(obj.id, self.exact_match.id)
        self.assertAlmostEqual(score, 1.0, places=6)

    def test_top_k_limits_results(self):
        query_vector = pad_vector([1.0, 0.0, 0.0])
        queryset = Candidate.objects.filter(user=self.user)

        ranked = similarity_search(queryset, query_vector, top_k=2)

        self.assertEqual(len(ranked), 2)
        self.assertEqual([obj.id for obj, _ in ranked], [self.exact_match.id, self.close_match.id])
