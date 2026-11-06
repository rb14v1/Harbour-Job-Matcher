import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { createJob, deleteJob, listJobs, updateJob } from "../../api/jobs";
import { extractErrorMessage } from "../../api/client";
import type { JobPosting } from "../../types";

export function JobsPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [editing, setEditing] = useState<JobPosting | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const res = await listJobs();
      setJobs(res.data.results);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function startEdit(job: JobPosting) {
    setEditing(job);
    setTitle(job.title);
    setDescription(job.description);
  }

  function resetForm() {
    setEditing(null);
    setTitle("");
    setDescription("");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (editing) {
        await updateJob(editing.id, { title, description });
      } else {
        await createJob({ title, description });
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
    if (!confirm("Delete this job posting?")) return;
    setError(null);
    try {
      await deleteJob(id);
      await load();
    } catch (err) {
      setError(extractErrorMessage(err));
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Job Postings</h1>
      </div>

      <div className="card">
        <form className="form-row" onSubmit={handleSubmit}>
          <label style={{ flex: 1 }}>
            Title
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
          <label style={{ flex: 2, width: "100%" }}>
            Description
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              required
            />
          </label>
          <button type="submit" disabled={submitting}>{editing ? "Save" : "Add job posting"}</button>
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
                <th>Title</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((job) => (
                <tr key={job.id}>
                  <td><Link to={`/jobs/${job.id}`}>{job.title}</Link></td>
                  <td>{new Date(job.created_at).toLocaleDateString()}</td>
                  <td className="actions">
                    <button className="secondary" onClick={() => startEdit(job)}>Edit</button>
                    <button className="danger" onClick={() => handleDelete(job.id)}>Delete</button>
                  </td>
                </tr>
              ))}
              {jobs.length === 0 && (
                <tr><td colSpan={3} className="muted">No job postings yet.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
