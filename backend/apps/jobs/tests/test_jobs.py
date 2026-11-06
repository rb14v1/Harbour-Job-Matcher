from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.common.test_utils import auth_client, create_user
from apps.jobs.models import JobPosting


class JobPostingCrudTests(APITestCase):
    def setUp(self):
        self.user = create_user(email="owner@example.com")
        self.client_auth = auth_client(self.user)

    def test_create_job_computes_embedding(self):
        url = reverse("jobposting-list")
        response = self.client_auth.post(url, {
            "title": "Backend Engineer",
            "description": "Python, Django, PostgreSQL.",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        job = JobPosting.objects.get(id=response.data["id"])
        self.assertIsNotNone(job.embedding)
        self.assertEqual(len(job.embedding), 1536)

    def test_list_only_returns_own_jobs(self):
        JobPosting.objects.create(user=self.user, title="Mine", description="desc")
        other = create_user(email="other@example.com")
        JobPosting.objects.create(user=other, title="Not mine", description="desc")

        response = self.client_auth.get(reverse("jobposting-list"))
        titles = [row["title"] for row in response.data["results"]]
        self.assertEqual(titles, ["Mine"])

    def test_requires_authentication(self):
        response = self.client.get(reverse("jobposting-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class JobPostingCrossUserIsolationTests(APITestCase):
    def setUp(self):
        self.user_a = create_user(email="a@example.com")
        self.user_b = create_user(email="b@example.com")
        self.client_a = auth_client(self.user_a)
        self.client_b = auth_client(self.user_b)

        self.job_a = JobPosting.objects.create(user=self.user_a, title="A's job", description="desc a")
        self.job_b = JobPosting.objects.create(user=self.user_b, title="B's job", description="desc b")

    def test_cannot_retrieve_other_users_job(self):
        response = self.client_b.get(reverse("jobposting-detail", args=[self.job_a.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_other_users_job(self):
        response = self.client_b.patch(
            reverse("jobposting-detail", args=[self.job_a.id]), {"title": "Hijacked"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.job_a.refresh_from_db()
        self.assertEqual(self.job_a.title, "A's job")

    def test_cannot_delete_other_users_job(self):
        response = self.client_b.delete(reverse("jobposting-detail", args=[self.job_a.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(JobPosting.objects.filter(id=self.job_a.id).exists())
