import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getJob, getJobMatches } from "../../api/jobs";
import { extractErrorMessage } from "../../api/client";
import type { JobMatchesResponse, JobPosting } from "../../types";

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const jobId = Number(id);

  const [job, setJob] = useState<JobPosting | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [k, setK] = useState(5);
  const [matching, setMatching] = useState(false);
  const [result, setResult] = useState<JobMatchesResponse | null>(null);

  useEffect(() => {
    setLoading(true);
    getJob(jobId)
      .then((res) => setJob(res.data))
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [jobId]);

  async function handleFindMatches() {
    setError(null);
    setMatching(true);
    setResult(null);
    try {
      const res = await getJobMatches(jobId, k);
      setResult(res.data);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setMatching(false);
    }
  }

  if (loading) return <p>Loading...</p>;
  if (error && !job) return <div className="form-error">{error}</div>;
  if (!job) return null;

  return (
    <div>
      <div className="page-header">
        <h1>{job.title}</h1>
        <Link to="/jobs">Back to job postings</Link>
      </div>

      <div className="card">
        <p>{job.description}</p>
      </div>

      <div className="card">
        <div className="form-row">
          <label>
            Top K
            <input
              type="number"
              min={1}
              max={50}
              value={k}
              onChange={(e) => setK(Number(e.target.value) || 5)}
              style={{ width: "5rem" }}
            />
          </label>
          <button onClick={handleFindMatches} disabled={matching}>
            {matching ? "Finding matches..." : "Find Matches"}
          </button>
        </div>
        {error && <div className="form-error">{error}</div>}
      </div>

      {result && (
        <div className="card">
          {result.stub_mode && (
            <div className="stub-mode-note">
              Running in stub mode — embeddings and the fit explanation below
              are generated deterministically without a real AI model, since
              no OPENAI_API_KEY is configured. Scores are reproducible but not
              semantically meaningful. Set OPENAI_API_KEY for real matching.
            </div>
          )}

          {result.matches.length === 0 ? (
            <p className="muted">No candidates to match against yet.</p>
          ) : (
            <>
              <h2>Ranked candidates</h2>
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Candidate</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {result.matches.map((match, index) => (
                    <tr key={match.candidate_id}>
                      <td>{index + 1}</td>
                      <td>{match.name}</td>
                      <td>{match.score.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="top-match-explanation">
                <h3>Top match fit explanation</h3>
                <p>{result.top_match_explanation}</p>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
