import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import ScoreBreakdown from '../ScoreBreakdown';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

describe('ScoreBreakdown', () => {
  const mockScores = {
    keyword_match: 85,
    relevance: 75,
    ats_score: 90,
    quality: 80,
  };

  it('should render all score categories', () => {
    render(<ScoreBreakdown scores={mockScores} />);
    
    expect(screen.getByText('Keyword Match')).toBeInTheDocument();
    expect(screen.getByText('Relevance')).toBeInTheDocument();
    expect(screen.getByText('ATS Compatibility')).toBeInTheDocument();
    expect(screen.getByText('Overall Quality')).toBeInTheDocument();
  });

  it('should display all scores', () => {
    render(<ScoreBreakdown scores={mockScores} />);
    
    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('90%')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
  });

  it('should show descriptions for each score', () => {
    render(<ScoreBreakdown scores={mockScores} />);
    
    expect(screen.getByText(/How well your resume matches job keywords/i)).toBeInTheDocument();
    expect(screen.getByText(/How relevant your experience is to the role/i)).toBeInTheDocument();
    expect(screen.getByText(/How well your resume passes ATS systems/i)).toBeInTheDocument();
    expect(screen.getByText(/General quality and formatting/i)).toBeInTheDocument();
  });

  it('should apply correct color classes based on scores', () => {
    const { container } = render(<ScoreBreakdown scores={mockScores} />);
    
    const scoreElements = container.querySelectorAll('.text-green-600, .text-blue-600, .text-yellow-600, .text-red-600');
    expect(scoreElements.length).toBeGreaterThan(0);
  });
});
