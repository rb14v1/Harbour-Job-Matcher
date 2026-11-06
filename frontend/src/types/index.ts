export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export interface JobPosting {
  id: number;
  title: string;
  description: string;
  created_at: string;
}

export interface Candidate {
  id: number;
  name: string;
  email: string;
  resume_text: string;
  created_at: string;
}

export interface JobMatch {
  candidate_id: number;
  name: string;
  score: number;
}

export interface JobMatchesResponse {
  matches: JobMatch[];
  top_match_explanation: string;
  stub_mode: boolean;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
