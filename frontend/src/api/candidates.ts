import { apiClient } from "./client";
import type { Candidate, Paginated } from "../types";

export function listCandidates() {
  return apiClient.get<Paginated<Candidate>>("/candidates/");
}

export function getCandidate(id: number) {
  return apiClient.get<Candidate>(`/candidates/${id}/`);
}

export function createCandidate(data: { name: string; email: string; resume_text: string }) {
  return apiClient.post<Candidate>("/candidates/", data);
}

export function updateCandidate(id: number, data: { name: string; email: string; resume_text: string }) {
  return apiClient.patch<Candidate>(`/candidates/${id}/`, data);
}

export function deleteCandidate(id: number) {
  return apiClient.delete(`/candidates/${id}/`);
}
