import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ApiClient } from '../api';

// Mock fetch
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('ApiClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('checkHealth', () => {
    it('should return health status', async () => {
      const mockResponse = { status: 'ok' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await ApiClient.checkHealth();
      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith('/api/health');
    });

    it('should throw error on failed health check', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
      });

      await expect(ApiClient.checkHealth()).rejects.toThrow('Health check failed');
    });
  });

  describe('checkApis', () => {
    it('should return available APIs', async () => {
      const mockResponse = { openai: true, gemini: false, claude: true };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await ApiClient.checkApis();
      expect(result).toEqual(mockResponse);
    });
  });

  describe('uploadResume', () => {
    it('should upload file successfully', async () => {
      const file = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
      const mockResponse = { file_path: 'uploads/resume.pdf', filename: 'resume.pdf' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await ApiClient.uploadResume(file);
      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/upload-resume',
        expect.objectContaining({ method: 'POST' })
      );
    });

    it('should throw error on upload failure', async () => {
      const file = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
      
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'File too large' }),
      });

      await expect(ApiClient.uploadResume(file)).rejects.toThrow('File too large');
    });
  });

  describe('analyzeResume', () => {
    it('should analyze resume successfully', async () => {
      const mockResponse = {
        extracted_data: { name: 'John Doe' },
        score: {
          total_score: 85,
          keyword_match_score: 90,
          keyword_match_details: {
            matched: ['Python', 'React'],
            missing: ['Docker'],
            match_percentage: 80,
          },
          relevance_score: 80,
          ats_score: 85,
          quality_score: 85,
          recommendations: ['Add Docker experience'],
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await ApiClient.analyzeResume('uploads/resume.pdf', 'Job description');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getDownloadUrl', () => {
    it('should return correct download URL', () => {
      const filename = 'resume.pdf';
      const url = ApiClient.getDownloadUrl(filename);
      expect(url).toBe('/api/download/resume.pdf');
    });
  });
});
