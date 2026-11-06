from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate
from apps.common.test_utils import auth_client, create_user


class CandidateCrudTests(APITestCase):
    def setUp(self):
        self.user = create_user(email="owner@example.com")
        self.client_auth = auth_client(self.user)

    def test_create_candidate_computes_embedding(self):
        url = reverse("candidate-list")
        response = self.client_auth.post(url, {
            "name": "Alice",
            "email": "alice@example.com",
            "resume_text": "Experienced backend developer with Django and PostgreSQL.",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        candidate = Candidate.objects.get(id=response.data["id"])
        self.assertIsNotNone(candidate.embedding)
        self.assertEqual(len(candidate.embedding), 1536)

    def test_update_recomputes_embedding(self):
        candidate = Candidate.objects.create(
            user=self.user, name="Alice", email="alice@example.com", resume_text="Original text."
        )
        original_embedding = list(candidate.embedding)

        url = reverse("candidate-detail", args=[candidate.id])
        response = self.client_auth.patch(url, {"resume_text": "Completely different text."})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        candidate.refresh_from_db()
        # pgvector-django returns VectorField values as numpy arrays on
        # Postgres (vs plain lists from SQLite's JSONField fallback);
        # comparing arrays directly raises "ambiguous truth value" under
        # assertNotEqual, so cast to list first to compare on either backend.
        self.assertNotEqual(list(candidate.embedding), original_embedding)

    def test_requires_authentication(self):
        response = self.client.get(reverse("candidate-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CandidateCrossUserIsolationTests(APITestCase):
    def setUp(self):
        self.user_a = create_user(email="a@example.com")
        self.user_b = create_user(email="b@example.com")
        self.client_a = auth_client(self.user_a)
        self.client_b = auth_client(self.user_b)

        self.candidate_a = Candidate.objects.create(
            user=self.user_a, name="A's candidate", email="a-cand@example.com", resume_text="desc a"
        )
        self.candidate_b = Candidate.objects.create(
            user=self.user_b, name="B's candidate", email="b-cand@example.com", resume_text="desc b"
        )

    def test_list_only_returns_own_candidates(self):
        response = self.client_a.get(reverse("candidate-list"))
        names = [row["name"] for row in response.data["results"]]
        self.assertEqual(names, ["A's candidate"])

    def test_cannot_retrieve_other_users_candidate(self):
        response = self.client_b.get(reverse("candidate-detail", args=[self.candidate_a.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_other_users_candidate(self):
        response = self.client_b.delete(reverse("candidate-detail", args=[self.candidate_a.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Candidate.objects.filter(id=self.candidate_a.id).exists())
