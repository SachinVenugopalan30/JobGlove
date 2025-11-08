import type { Score, AnalyzeResponse } from './score';

export type { AnalyzeResponse } from './score';

export interface ApiError {
  error: string;
}

export interface TailorRequest {
  file_path: string;
  job_description: string;
  api: 'openai' | 'gemini' | 'claude';
  user_name: string;
  company: string;
  job_title: string;
  custom_prompt?: string;
}

export interface TailorResponse {
  pdf_file: string;
  tex_file: string;
  original_text: string;
  tailored_text: string;
  tailored_score: Score;
  message: string;
}
