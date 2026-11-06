import { apiClient } from "./client";
import type { JobMatchesResponse, JobPosting, Paginated } from "../types";

export function listJobs() {
  return apiClient.get<Paginated<JobPosting>>("/jobs/");
}

export function getJob(id: number) {
  return apiClient.get<JobPosting>(`/jobs/${id}/`);
}

export function createJob(data: { title: string; description: string }) {
  return apiClient.post<JobPosting>("/jobs/", data);
}

export function updateJob(id: number, data: { title: string; description: string }) {
  return apiClient.patch<JobPosting>(`/jobs/${id}/`, data);
}

export function deleteJob(id: number) {
  return apiClient.delete(`/jobs/${id}/`);
}

export function getJobMatches(id: number, k = 5) {
  return apiClient.get<JobMatchesResponse>(`/jobs/${id}/matches/`, { params: { k } });
}
