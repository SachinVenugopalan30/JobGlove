import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Tailor from '../Tailor';

vi.mock('../../../components/tailor/TailorForm', () => ({
  default: ({ onComplete }: any) => (
    <div data-testid="tailor-form">
      <button onClick={() => onComplete({ original_score: {}, tailored_score: {}, pdf_file: '', tex_file: '' })}>
        Submit Form
      </button>
    </div>
  ),
}));

vi.mock('../../../components/tailor/ResultsView', () => ({
  default: ({ onReset }: any) => (
    <div data-testid="results-view">
      <button onClick={onReset}>Reset</button>
    </div>
  ),
}));

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('Tailor Page (Simplified)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderTailorPage = () => {
    return render(
      <BrowserRouter>
        <Tailor />
      </BrowserRouter>
    );
  };

  describe('Initial Rendering', () => {
    it('renders the page header', () => {
      renderTailorPage();

      expect(screen.getByText('JobGlove')).toBeInTheDocument();
    });

    it('renders back button', () => {
      renderTailorPage();

      const backButton = screen.getByRole('button', { name: /Back/i });
      expect(backButton).toBeInTheDocument();
    });

    it('back button navigates to home', () => {
      renderTailorPage();

      const backButton = screen.getByRole('button', { name: /Back/i });
      fireEvent.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/');
    });

    it('shows TailorForm initially', () => {
      renderTailorPage();

      expect(screen.getByTestId('tailor-form')).toBeInTheDocument();
      expect(screen.queryByTestId('results-view')).not.toBeInTheDocument();
    });
  });

  describe('State Management', () => {
    it('switches to ResultsView after form completion', async () => {
      renderTailorPage();

      const submitButton = screen.getByRole('button', { name: /Submit Form/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('results-view')).toBeInTheDocument();
        expect(screen.queryByTestId('tailor-form')).not.toBeInTheDocument();
      });
    });

    it('switches back to TailorForm after reset', async () => {
      renderTailorPage();

      const submitButton = screen.getByRole('button', { name: /Submit Form/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByTestId('results-view')).toBeInTheDocument();
      });

      const resetButton = screen.getByRole('button', { name: /Reset/i });
      fireEvent.click(resetButton);

      await waitFor(() => {
        expect(screen.getByTestId('tailor-form')).toBeInTheDocument();
        expect(screen.queryByTestId('results-view')).not.toBeInTheDocument();
      });
    });

    it('passes results data to ResultsView', async () => {
      const mockResults = {
        original_score: {
          total_score: 70,
          keyword_match_score: 65,
          relevance_score: 75,
          ats_score: 70,
          quality_score: 70,
        },
        tailored_score: {
          total_score: 90,
          keyword_match_score: 95,
          relevance_score: 88,
          ats_score: 92,
          quality_score: 87,
        },
        pdf_file: 'resume.pdf',
        tex_file: 'resume.tex',
      };

      vi.resetModules();
      vi.doMock('../../../components/tailor/TailorForm', () => ({
        default: ({ onComplete }: any) => (
          <div data-testid="tailor-form">
            <button onClick={() => onComplete(mockResults)}>Submit Form</button>
          </div>
        ),
      }));

      vi.doMock('../../../components/tailor/ResultsView', () => ({
        default: ({ results }: any) => (
          <div data-testid="results-view">
            <div>Original: {results.original_score.total_score}</div>
            <div>Tailored: {results.tailored_score.total_score}</div>
          </div>
        ),
      }));

      const Tailor = (await import('../Tailor')).default;

      render(
        <BrowserRouter>
          <Tailor />
        </BrowserRouter>
      );

      const submitButton = screen.getByRole('button', { name: /Submit Form/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Original: 70')).toBeInTheDocument();
        expect(screen.getByText('Tailored: 90')).toBeInTheDocument();
      });
    });
  });

  describe('Animation', () => {
    it('applies fade-in animation', () => {
      renderTailorPage();

      const mainContent = screen.getByTestId('tailor-form').parentElement;
      expect(mainContent).toBeInTheDocument();
    });
  });

  describe('No Multi-Step Flow', () => {
    it('does not render StepIndicator', () => {
      renderTailorPage();

      expect(screen.queryByText(/Upload/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Analyze/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Step 1/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Step 2/i)).not.toBeInTheDocument();
    });

    it('does not have multiple steps', () => {
      renderTailorPage();

      const form = screen.getByTestId('tailor-form');
      expect(form).toBeInTheDocument();

      const steps = screen.queryAllByText(/Step/i);
      expect(steps.length).toBe(0);
    });
  });
});
