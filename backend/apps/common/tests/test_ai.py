from django.conf import settings
from django.test import TestCase

from apps.common.ai import generate_answer, get_embedding, is_stub_mode


class EmbeddingStubTests(TestCase):
    def test_stub_mode_is_active_without_api_key(self):
        # No OPENAI_API_KEY is configured in this test environment.
        self.assertTrue(is_stub_mode())

    def test_embedding_has_configured_dimensions(self):
        vector = get_embedding("Backend Engineer with Python experience")
        self.assertEqual(len(vector), settings.EMBEDDING_DIMENSIONS)

    def test_embedding_is_deterministic_for_same_text(self):
        text = "Experienced Django developer, PostgreSQL, REST APIs"
        first = get_embedding(text)
        second = get_embedding(text)
        self.assertEqual(first, second)

    def test_embedding_differs_for_different_text(self):
        first = get_embedding("Backend Engineer")
        second = get_embedding("Frontend Engineer")
        self.assertNotEqual(first, second)

    def test_embedding_values_within_expected_range(self):
        vector = get_embedding("Some resume text")
        self.assertTrue(all(-1.0 <= v <= 1.0 for v in vector))

    def test_embedding_is_l2_normalized(self):
        vector = get_embedding("Some resume text")
        magnitude = sum(v * v for v in vector) ** 0.5
        self.assertAlmostEqual(magnitude, 1.0, places=6)


class GenerateAnswerStubTests(TestCase):
    def test_stub_format_with_candidates(self):
        answer = generate_answer("Backend Engineer", ["Experienced Python developer."])
        self.assertTrue(answer.startswith("[STUB AI RESPONSE"))
        self.assertIn("Based on 1 candidate(s)", answer)
        self.assertIn("Experienced Python developer.", answer)

    def test_stub_format_with_no_candidates(self):
        answer = generate_answer("Backend Engineer", [])
        self.assertTrue(answer.startswith("[STUB AI RESPONSE"))
        self.assertIn("Based on 0 candidate(s): none", answer)
