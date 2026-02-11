import type { AnalyzeResponse, TailorRequest, TailorResponse, ApiError } from '@/types/api';
import type { UploadResponse } from '@/types/resume';

const API_BASE = '/api';

export class ApiClient {
  /**
   * Check which AI APIs are available in the backend
   */
  static async checkApis(): Promise<Record<string, boolean>> {
    const response = await fetch(`${API_BASE}/check-apis`);
    if (!response.ok) throw new Error('Failed to check APIs');
    return response.json();
  }

  /**
   * Upload a resume file to the backend
   */
  static async uploadResume(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload-resume`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json() as ApiError;
      throw new Error(error.error || 'Upload failed');
    }

    return response.json();
  }

  /**
   * Analyze a resume against a job description
   */
  static async analyzeResume(
    filePath: string,
    jobDescription: string
  ): Promise<AnalyzeResponse> {
    const response = await fetch(`${API_BASE}/analyze-resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_path: filePath,
        job_description: jobDescription,
      }),
    });

    if (!response.ok) {
      const error = await response.json() as ApiError;
      throw new Error(error.error || 'Analysis failed');
    }

    return response.json();
  }

  /**
   * Tailor a resume using AI
   */
  static async tailorResume(data: TailorRequest): Promise<TailorResponse> {
    const response = await fetch(`${API_BASE}/tailor-resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json() as ApiError;
      throw new Error(error.error || 'Tailoring failed');
    }

    return response.json();
  }

  /**
   * Get the download URL for a file
   */
  static getDownloadUrl(filename: string): string {
    return `${API_BASE}/download/${filename}`;
  }

  /**
   * Check backend health
   */
  static async checkHealth(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  }
}
