"""
AI layer with a dual real/stub path, switched purely by whether
OPENAI_API_KEY is set in the environment:

- Set: calls the real OpenAI API (embeddings + chat completions).
- Unset (default for this build - no API key is available here): falls
  back to a deterministic, offline stub for both functions, so the whole
  pipeline (embeddings -> storage -> similarity search -> explanation) is
  fully testable with zero network access and zero API cost.

IMPORTANT: the stub embedding is NOT semantically meaningful. It is a
reproducible pseudo-random vector derived from a hash of the input text -
identical text always produces the identical vector (so storage/search
code can be exercised deterministically), but it carries no information
about the text's actual meaning. Similarity scores computed from stub
embeddings are therefore meaningless for real job/resume matching; they
only prove the plumbing works end to end. Real match quality requires a
real OPENAI_API_KEY.
"""
import hashlib
import os
import random

from django.conf import settings


def is_stub_mode() -> bool:
    return not bool(os.environ.get("OPENAI_API_KEY"))


def get_embedding(text: str) -> list[float]:
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key:
        import openai

        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
            dimensions=settings.EMBEDDING_DIMENSIONS,
        )
        return response.data[0].embedding

    # --- Deterministic stub (no API key configured) -----------------------
    # Seeded from a sha256 hash of the text so the same input always yields
    # the same vector (reproducible for tests/seed data), without ever
    # calling out to a real embeddings model.
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    rng = random.Random(digest)
    vector = [rng.uniform(-1.0, 1.0) for _ in range(settings.EMBEDDING_DIMENSIONS)]
    norm = math_sqrt_sum_of_squares(vector)
    if norm == 0:
        return vector
    return [v / norm for v in vector]


def math_sqrt_sum_of_squares(vector: list[float]) -> float:
    return sum(v * v for v in vector) ** 0.5


def generate_answer(question: str, context_snippets: list[str]) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key:
        import openai

        client = openai.OpenAI(api_key=api_key)
        context_block = "\n\n".join(context_snippets) if context_snippets else "(no candidates provided)"
        response = client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You explain why a candidate resume is or isn't a good fit for a job posting.",
                },
                {
                    "role": "user",
                    "content": f"Job: {question}\n\nCandidate resume(s):\n{context_block}\n\n"
                    "Explain in 2-3 sentences why the top candidate fits this job.",
                },
            ],
        )
        return response.choices[0].message.content

    # --- Deterministic templated stub (no API key configured) -------------
    first_snippet = context_snippets[0][:200] if context_snippets else "none"
    return (
        f"[STUB AI RESPONSE — set OPENAI_API_KEY for real output] "
        f"Based on {len(context_snippets)} candidate(s): {first_snippet}"
    )
