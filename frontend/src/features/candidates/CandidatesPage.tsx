import { useEffect, useState } from "react";

import { createCandidate, deleteCandidate, listCandidates, updateCandidate } from "../../api/candidates";
import { extractErrorMessage } from "../../api/client";
import type { Candidate } from "../../types";

export function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editing, setEditing] = useState<Candidate | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res = await listCandidates();
      setCandidates(res.data.results);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function startEdit(candidate: Candidate) {
    setEditing(candidate);
    setName(candidate.name);
    setEmail(candidate.email);
    setResumeText(candidate.resume_text);
  }

  function resetForm() {
    setEditing(null);
    setName("");
    setEmail("");
    setResumeText("");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (editing) {
        await updateCandidate(editing.id, { name, email, resume_text: resumeText });
      } else {
        await createCandidate({ name, email, resume_text: resumeText });
      }
      resetForm();
      await load();
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this candidate?")) return;
    setError(null);
    try {
      await deleteCandidate(id);
      await load();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Candidates</h1>
      </div>

      <div className="card">
        <form className="form-row" onSubmit={handleSubmit}>
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label>
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label style={{ flex: 2, width: "100%" }}>
            Resume text
            <textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              rows={4}
              required
            />
          </label>
          <button type="submit" disabled={submitting}>{editing ? "Save" : "Add candidate"}</button>
          {editing && <button type="button" className="secondary" onClick={resetForm}>Cancel</button>}
        </form>
        {error && <div className="form-error">{error}</div>}
      </div>

      <div className="card">
        {loading ? (
          <p>Loading...</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.email}</td>
                  <td>{new Date(c.created_at).toLocaleDateString()}</td>
                  <td className="actions">
                    <button className="secondary" onClick={() => startEdit(c)}>Edit</button>
                    <button className="danger" onClick={() => handleDelete(c.id)}>Delete</button>
                  </td>
                </tr>
              ))}
              {candidates.length === 0 && (
                <tr><td colSpan={4} className="muted">No candidates yet.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
