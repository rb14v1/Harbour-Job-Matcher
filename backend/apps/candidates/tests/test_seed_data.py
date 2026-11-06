from django.test import TestCase

from apps.accounts.models import User
from apps.candidates.models import Candidate
from apps.jobs.models import JobPosting


class SeedDataMigrationTests(TestCase):
    """The Django test runner builds the test database by running every
    migration, including apps/candidates/migrations/0002_seed_demo_data.py,
    so the demo seed data is expected to already exist here - this is not a
    fixture, it's verifying the actual seed migration ran correctly."""

    def test_demo_user_exists_with_expected_password(self):
        user = User.objects.get(email="demo@example.com")
        self.assertTrue(user.check_password("demo12345"))

    def test_seed_job_posting_count(self):
        user = User.objects.get(email="demo@example.com")
        self.assertEqual(JobPosting.objects.filter(user=user).count(), 5)

    def test_seed_candidate_count(self):
        user = User.objects.get(email="demo@example.com")
        self.assertEqual(Candidate.objects.filter(user=user).count(), 12)

    def test_seed_job_postings_have_full_length_embeddings(self):
        user = User.objects.get(email="demo@example.com")
        for job in JobPosting.objects.filter(user=user):
            self.assertIsNotNone(job.embedding)
            self.assertEqual(len(job.embedding), 1536)

    def test_seed_candidates_have_full_length_embeddings(self):
        user = User.objects.get(email="demo@example.com")
        for candidate in Candidate.objects.filter(user=user):
            self.assertIsNotNone(candidate.embedding)
            self.assertEqual(len(candidate.embedding), 1536)

    def test_seed_candidates_have_realistic_varied_text(self):
        user = User.objects.get(email="demo@example.com")
        resumes = list(Candidate.objects.filter(user=user).values_list("resume_text", flat=True))
        # Expect meaningfully long, distinct resume text (not placeholder rows).
        self.assertTrue(all(len(text) > 100 for text in resumes))
        self.assertEqual(len(set(resumes)), len(resumes))
