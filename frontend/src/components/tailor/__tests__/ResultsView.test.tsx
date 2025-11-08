import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ResultsView from '../ResultsView';

describe('ResultsView', () => {
  const mockOnReset = vi.fn();

  const mockResults = {
    original_score: {
      total_score: 72,
      keyword_match_score: 68,
      relevance_score: 75,
      ats_score: 80,
      quality_score: 65,
      recommendations: ['Add more metrics', 'Use action verbs', 'Include certifications'],
    },
    tailored_score: {
      total_score: 89,
      keyword_match_score: 92,
      relevance_score: 88,
      ats_score: 85,
      quality_score: 90,
    },
    pdf_file: 'resume_12345.pdf',
    tex_file: 'resume_12345.tex',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    delete window.location;
    window.location = { ...window.location };
    window.open = vi.fn();
  });

  describe('Rendering', () => {
    it('renders success message', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      expect(screen.getByText(/Resume Successfully Tailored/i)).toBeInTheDocument();
    });

    it('displays both original and tailored scores', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      expect(screen.getByText('Original Resume')).toBeInTheDocument();
      expect(screen.getByText('Tailored Resume')).toBeInTheDocument();
    });

    it('shows score improvement', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const improvement = mockResults.tailored_score.total_score - mockResults.original_score.total_score;
      expect(screen.getByText(`+${improvement}`)).toBeInTheDocument();
    });

    it('displays score breakdown categories', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      expect(screen.getByText('Keyword Match')).toBeInTheDocument();
      expect(screen.getByText('Relevance')).toBeInTheDocument();
      expect(screen.getByText('ATS Score')).toBeInTheDocument();
      expect(screen.getByText('Quality')).toBeInTheDocument();
    });
  });

  describe('Score Display', () => {
    it('shows correct original score values', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const scoreElements = screen.getAllByText('68');
      expect(scoreElements.length).toBeGreaterThan(0);
    });

    it('shows correct tailored score values', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const scoreElements = screen.getAllByText('92');
      expect(scoreElements.length).toBeGreaterThan(0);
    });

    it('displays all breakdown scores', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      expect(screen.getByText('68')).toBeInTheDocument();
      expect(screen.getByText('92')).toBeInTheDocument();
      expect(screen.getByText('75')).toBeInTheDocument();
      expect(screen.getByText('88')).toBeInTheDocument();
      expect(screen.getByText('80')).toBeInTheDocument();
      expect(screen.getByText('85')).toBeInTheDocument();
      expect(screen.getByText('65')).toBeInTheDocument();
      expect(screen.getByText('90')).toBeInTheDocument();
    });
  });

  describe('Recommendations', () => {
    it('displays recommendations section when available', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      expect(screen.getByText(/Original Resume Insights/i)).toBeInTheDocument();
    });

    it('shows all recommendations', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      expect(screen.getByText('Add more metrics')).toBeInTheDocument();
      expect(screen.getByText('Use action verbs')).toBeInTheDocument();
      expect(screen.getByText('Include certifications')).toBeInTheDocument();
    });

    it('does not show recommendations section when none available', () => {
      const resultsWithoutRecs = {
        ...mockResults,
        original_score: {
          ...mockResults.original_score,
          recommendations: undefined,
        },
      };

      render(<ResultsView results={resultsWithoutRecs} onReset={mockOnReset} />);

      expect(screen.queryByText(/Original Resume Insights/i)).not.toBeInTheDocument();
    });

    it('does not show section when recommendations array is empty', () => {
      const resultsWithEmptyRecs = {
        ...mockResults,
        original_score: {
          ...mockResults.original_score,
          recommendations: [],
        },
      };

      render(<ResultsView results={resultsWithEmptyRecs} onReset={mockOnReset} />);

      expect(screen.queryByText(/Original Resume Insights/i)).not.toBeInTheDocument();
    });
  });

  describe('Download Buttons', () => {
    it('renders PDF download button', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const pdfButton = screen.getByRole('button', { name: /Download PDF/i });
      expect(pdfButton).toBeInTheDocument();
    });

    it('renders LaTeX download button', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const texButton = screen.getByRole('button', { name: /Download LaTeX/i });
      expect(texButton).toBeInTheDocument();
    });

    it('PDF button triggers download', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const pdfButton = screen.getByRole('button', { name: /Download PDF/i });
      fireEvent.click(pdfButton);

      expect(window.open).toHaveBeenCalledWith('/api/download/resume_12345.pdf', '_blank');
    });

    it('LaTeX button triggers download', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const texButton = screen.getByRole('button', { name: /Download LaTeX/i });
      fireEvent.click(texButton);

      expect(window.open).toHaveBeenCalledWith('/api/download/resume_12345.tex', '_blank');
    });
  });

  describe('Reset Functionality', () => {
    it('renders reset button', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const resetButton = screen.getByRole('button', { name: /Tailor Another Resume/i });
      expect(resetButton).toBeInTheDocument();
    });

    it('calls onReset when button is clicked', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const resetButton = screen.getByRole('button', { name: /Tailor Another Resume/i });
      fireEvent.click(resetButton);

      expect(mockOnReset).toHaveBeenCalledTimes(1);
    });
  });

  describe('Score Improvement Indicator', () => {
    it('shows positive improvement', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      expect(screen.getByText('+17')).toBeInTheDocument();
    });

    it('shows no improvement when scores are equal', () => {
      const equalResults = {
        ...mockResults,
        original_score: { ...mockResults.original_score, total_score: 89 },
      };

      render(<ResultsView results={equalResults} onReset={mockOnReset} />);

      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('shows negative improvement correctly', () => {
      const worseResults = {
        ...mockResults,
        tailored_score: { ...mockResults.tailored_score, total_score: 60 },
      };

      render(<ResultsView results={worseResults} onReset={mockOnReset} />);

      expect(screen.getByText('-12')).toBeInTheDocument();
    });

    it('applies correct styling for positive improvement', () => {
      render(<ResultsView results={mockResults} onReset={mockOnReset} />);

      const badge = screen.getByText('+17');
      expect(badge).toHaveClass('text-green-600');
    });
  });

  describe('Edge Cases', () => {
    it('handles zero scores', () => {
      const zeroResults = {
        ...mockResults,
        original_score: {
          total_score: 0,
          keyword_match_score: 0,
          relevance_score: 0,
          ats_score: 0,
          quality_score: 0,
        },
        tailored_score: {
          total_score: 0,
          keyword_match_score: 0,
          relevance_score: 0,
          ats_score: 0,
          quality_score: 0,
        },
      };

      render(<ResultsView results={zeroResults} onReset={mockOnReset} />);

      expect(screen.getAllByText('0').length).toBeGreaterThan(0);
    });

    it('handles maximum scores', () => {
      const maxResults = {
        ...mockResults,
        original_score: {
          total_score: 100,
          keyword_match_score: 100,
          relevance_score: 100,
          ats_score: 100,
          quality_score: 100,
        },
        tailored_score: {
          total_score: 100,
          keyword_match_score: 100,
          relevance_score: 100,
          ats_score: 100,
          quality_score: 100,
        },
      };

      render(<ResultsView results={maxResults} onReset={mockOnReset} />);

      expect(screen.getAllByText('100').length).toBeGreaterThan(0);
    });

    it('handles long filenames', () => {
      const longFilenameResults = {
        ...mockResults,
        pdf_file: 'very_long_filename_with_lots_of_characters_12345678.pdf',
        tex_file: 'very_long_filename_with_lots_of_characters_12345678.tex',
      };

      render(<ResultsView results={longFilenameResults} onReset={mockOnReset} />);

      const pdfButton = screen.getByRole('button', { name: /Download PDF/i });
      fireEvent.click(pdfButton);

      expect(window.open).toHaveBeenCalledWith(
        '/api/download/very_long_filename_with_lots_of_characters_12345678.pdf',
        '_blank'
      );
    });
  });
});
