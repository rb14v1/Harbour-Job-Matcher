from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate
from apps.common.test_utils import auth_client, create_user
from apps.jobs.models import JobPosting


class JobMatchesTests(APITestCase):
    def setUp(self):
        self.user = create_user(email="recruiter@example.com")
        self.client_auth = auth_client(self.user)

        self.job = JobPosting.objects.create(
            user=self.user,
            title="Backend Engineer",
            description="Python, Django, PostgreSQL, REST APIs.",
        )
        self.candidate_a = Candidate.objects.create(
            user=self.user,
            name="Alice",
            email="alice@example.com",
            resume_text="Experienced Django and PostgreSQL backend developer.",
        )
        self.candidate_b = Candidate.objects.create(
            user=self.user,
            name="Bob",
            email="bob@example.com",
            resume_text="Graphic designer with Photoshop and Illustrator experience.",
        )

    def test_matches_response_shape(self):
        url = reverse("jobposting-matches", args=[self.job.id])
        response = self.client_auth.get(url, {"k": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("matches", response.data)
        self.assertIn("top_match_explanation", response.data)
        self.assertIn("stub_mode", response.data)
        self.assertTrue(response.data["stub_mode"])

        self.assertEqual(len(response.data["matches"]), 2)
        for row in response.data["matches"]:
            self.assertIn("candidate_id", row)
            self.assertIn("name", row)
            self.assertIn("score", row)

    def test_matches_respects_k(self):
        url = reverse("jobposting-matches", args=[self.job.id])
        response = self.client_auth.get(url, {"k": 1})
        self.assertEqual(len(response.data["matches"]), 1)

    def test_top_match_explanation_is_stub_formatted(self):
        url = reverse("jobposting-matches", args=[self.job.id])
        response = self.client_auth.get(url, {"k": 5})
        explanation = response.data["top_match_explanation"]
        self.assertTrue(explanation.startswith("[STUB AI RESPONSE"))
        self.assertIn("Based on 1 candidate(s)", explanation)

    def test_matches_with_no_candidates_returns_empty(self):
        Candidate.objects.filter(user=self.user).delete()
        url = reverse("jobposting-matches", args=[self.job.id])
        response = self.client_auth.get(url, {"k": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["matches"], [])
        self.assertEqual(response.data["top_match_explanation"], "")

    def test_matches_requires_authentication(self):
        url = reverse("jobposting-matches", args=[self.job.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JobMatchesCrossUserIsolationTests(APITestCase):
    """A user's matches must never include another user's candidates, and a
    user must never be able to run /matches/ against another user's job."""

    def setUp(self):
        self.user_a = create_user(email="a@example.com")
        self.user_b = create_user(email="b@example.com")
        self.client_a = auth_client(self.user_a)
        self.client_b = auth_client(self.user_b)

        self.job_a = JobPosting.objects.create(
            user=self.user_a, title="Backend Engineer", description="Python, Django, PostgreSQL."
        )
        self.job_b = JobPosting.objects.create(
            user=self.user_b, title="Backend Engineer", description="Python, Django, PostgreSQL."
        )

        self.candidate_a = Candidate.objects.create(
            user=self.user_a, name="Alice (A's candidate)", email="alice@example.com",
            resume_text="Django and PostgreSQL backend developer.",
        )
        self.candidate_b = Candidate.objects.create(
            user=self.user_b, name="Bob (B's candidate)", email="bob@example.com",
            resume_text="Django and PostgreSQL backend developer.",
        )

    def test_matches_for_own_job_only_include_own_candidates(self):
        url = reverse("jobposting-matches", args=[self.job_a.id])
        response = self.client_a.get(url, {"k": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {row["candidate_id"] for row in response.data["matches"]}
        self.assertEqual(returned_ids, {self.candidate_a.id})
        self.assertNotIn(self.candidate_b.id, returned_ids)

    def test_cannot_run_matches_against_other_users_job(self):
        url = reverse("jobposting-matches", args=[self.job_b.id])
        response = self.client_a.get(url, {"k": 10})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
