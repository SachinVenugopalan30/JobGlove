import { describe, it, expect } from 'vitest';
import { cn, getScoreColor, getScoreGradient, formatFileSize } from '../utils';

describe('Utils', () => {
  describe('cn', () => {
    it('should merge class names correctly', () => {
      expect(cn('px-4', 'py-2')).toBe('px-4 py-2');
    });

    it('should handle conditional classes', () => {
      expect(cn('base', false && 'conditional')).toBe('base');
      expect(cn('base', true && 'conditional')).toBe('base conditional');
    });

    it('should override conflicting classes', () => {
      expect(cn('px-4', 'px-6')).toBe('px-6');
    });
  });

  describe('getScoreColor', () => {
    it('should return green for scores >= 80', () => {
      expect(getScoreColor(80)).toBe('text-green-600');
      expect(getScoreColor(100)).toBe('text-green-600');
    });

    it('should return blue for scores >= 60 and < 80', () => {
      expect(getScoreColor(60)).toBe('text-blue-600');
      expect(getScoreColor(79)).toBe('text-blue-600');
    });

    it('should return yellow for scores >= 40 and < 60', () => {
      expect(getScoreColor(40)).toBe('text-yellow-600');
      expect(getScoreColor(59)).toBe('text-yellow-600');
    });

    it('should return red for scores < 40', () => {
      expect(getScoreColor(0)).toBe('text-red-600');
      expect(getScoreColor(39)).toBe('text-red-600');
    });
  });

  describe('getScoreGradient', () => {
    it('should return green gradient for high scores', () => {
      const result = getScoreGradient(80);
      expect(result.className).toBe('from-green-500 to-emerald-600');
      expect(result.from).toBeDefined();
      expect(result.to).toBeDefined();
    });

    it('should return blue gradient for medium-high scores', () => {
      const result = getScoreGradient(60);
      expect(result.className).toBe('from-blue-500 to-indigo-600');
      expect(result.from).toBeDefined();
      expect(result.to).toBeDefined();
    });

    it('should return yellow gradient for medium scores', () => {
      const result = getScoreGradient(40);
      expect(result.className).toBe('from-yellow-500 to-orange-600');
      expect(result.from).toBeDefined();
      expect(result.to).toBeDefined();
    });

    it('should return red gradient for low scores', () => {
      const result = getScoreGradient(30);
      expect(result.className).toBe('from-red-500 to-rose-600');
      expect(result.from).toBeDefined();
      expect(result.to).toBeDefined();
    });
  });

  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(500)).toBe('500 Bytes');
    });

    it('should format KB correctly', () => {
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1536)).toBe('1.5 KB');
    });

    it('should format MB correctly', () => {
      expect(formatFileSize(1048576)).toBe('1 MB');
      expect(formatFileSize(2097152)).toBe('2 MB');
    });
  });
});
