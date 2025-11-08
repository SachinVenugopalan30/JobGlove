import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TailorForm from '../TailorForm';

global.fetch = vi.fn();

describe('TailorForm', () => {
  const mockOnComplete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ openai: true, gemini: false, claude: true }),
    });
  });

  describe('Rendering', () => {
    it('renders the form with all fields', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => {
        expect(screen.getByText(/Tailor Your Resume/i)).toBeInTheDocument();
      });

      expect(screen.getByLabelText(/Resume Upload/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Job Title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Company/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Job Description/i)).toBeInTheDocument();
      expect(screen.getByText(/AI Provider/i)).toBeInTheDocument();
    });

    it('displays submit button', () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      expect(screen.getByRole('button', { name: /Tailor Resume with AI/i })).toBeInTheDocument();
    });

    it('submit button is disabled initially', () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const button = screen.getByRole('button', { name: /Tailor Resume with AI/i });
      expect(button).toBeDisabled();
    });
  });

  describe('File Upload', () => {
    it('accepts file upload via input', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const file = new File(['resume content'], 'resume.pdf', { type: 'application/pdf' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText('resume.pdf')).toBeInTheDocument();
      });
    });

    it('accepts DOCX files', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const file = new File(['resume content'], 'resume.docx', {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText('resume.docx')).toBeInTheDocument();
      });
    });

    it('rejects invalid file types', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const file = new File(['resume content'], 'resume.txt', { type: 'text/plain' });
      const input = document.querySelector('input[type="file"]') as HTMLInputElement;

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText(/Please upload a PDF or DOCX file/i)).toBeInTheDocument();
      });
    });

    it('accepts file via drag and drop', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const file = new File(['resume content'], 'resume.pdf', { type: 'application/pdf' });
      const dropZone = screen.getByText(/Click or drag to upload/i).closest('div');

      fireEvent.drop(dropZone!, {
        dataTransfer: {
          files: [file],
        },
      });

      await waitFor(() => {
        expect(screen.getByText('resume.pdf')).toBeInTheDocument();
      });
    });
  });

  describe('Form Fields', () => {
    it('allows entering job title', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const input = screen.getByPlaceholderText(/Software Engineer/i);
      await userEvent.type(input, 'Senior Developer');

      expect(input).toHaveValue('Senior Developer');
    });

    it('allows entering company name', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const input = screen.getByPlaceholderText(/Google/i);
      await userEvent.type(input, 'Microsoft');

      expect(input).toHaveValue('Microsoft');
    });

    it('allows entering job description', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const textarea = screen.getByPlaceholderText(/Paste the full job description/i);
      await userEvent.type(textarea, 'Looking for a talented developer...');

      expect(textarea).toHaveValue('Looking for a talented developer...');
    });
  });

  describe('AI Provider Selection', () => {
    it('displays available AI providers', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => {
        expect(screen.getByText('openai')).toBeInTheDocument();
        expect(screen.getByText('claude')).toBeInTheDocument();
      });
    });

    it('auto-selects first available provider', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => {
        const openaiButton = screen.getByText('openai').closest('button');
        expect(openaiButton).toHaveClass('border-primary');
      });
    });

    it('allows selecting different provider', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => {
        const claudeButton = screen.getByText('claude').closest('button');
        fireEvent.click(claudeButton!);
      });

      const claudeButton = screen.getByText('claude').closest('button');
      expect(claudeButton).toHaveClass('border-primary');
    });

    it('disables unavailable providers', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => {
        const geminiButton = screen.getByText('gemini').closest('button');
        expect(geminiButton).toBeDisabled();
      });
    });
  });

  describe('Form Validation', () => {
    it('enables submit when all fields are filled', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const file = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      await userEvent.upload(fileInput, file);

      const titleInput = screen.getByPlaceholderText(/Software Engineer/i);
      await userEvent.type(titleInput, 'Developer');

      const companyInput = screen.getByPlaceholderText(/Google/i);
      await userEvent.type(companyInput, 'Company');

      const descInput = screen.getByPlaceholderText(/Paste the full job description/i);
      await userEvent.type(descInput, 'Job description');

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /Tailor Resume with AI/i });
        expect(button).not.toBeDisabled();
      });
    });

    it('shows error when submitting without file', async () => {
      render(<TailorForm onComplete={mockOnComplete} />);

      const titleInput = screen.getByPlaceholderText(/Software Engineer/i);
      await userEvent.type(titleInput, 'Developer');

      const companyInput = screen.getByPlaceholderText(/Google/i);
      await userEvent.type(companyInput, 'Company');

      const descInput = screen.getByPlaceholderText(/Paste the full job description/i);
      await userEvent.type(descInput, 'Job description');

      const button = screen.getByRole('button', { name: /Tailor Resume with AI/i });
      expect(button).toBeDisabled();
    });
  });

  describe('Form Submission', () => {
    const setupFilledForm = async () => {
      const file = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      await userEvent.upload(fileInput, file);

      const titleInput = screen.getByPlaceholderText(/Software Engineer/i);
      await userEvent.type(titleInput, 'Developer');

      const companyInput = screen.getByPlaceholderText(/Google/i);
      await userEvent.type(companyInput, 'TestCo');

      const descInput = screen.getByPlaceholderText(/Paste the full job description/i);
      await userEvent.type(descInput, 'Job description here');
    };

    it('submits form successfully', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ openai: true, gemini: false, claude: true }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ file_path: 'uploads/resume.pdf' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            original_score: { total_score: 70 },
            tailored_score: { total_score: 90 },
            pdf_file: 'resume.pdf',
            tex_file: 'resume.tex',
          }),
        });

      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => screen.getByText('openai'));
      await setupFilledForm();

      const button = screen.getByRole('button', { name: /Tailor Resume with AI/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledWith({
          original_score: { total_score: 70 },
          tailored_score: { total_score: 90 },
          pdf_file: 'resume.pdf',
          tex_file: 'resume.tex',
        });
      });
    });

    it('shows loading state during submission', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ openai: true }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ file_path: 'uploads/resume.pdf' }),
        })
        .mockImplementationOnce(
          () =>
            new Promise((resolve) =>
              setTimeout(
                () =>
                  resolve({
                    ok: true,
                    json: async () => ({ original_score: {}, tailored_score: {}, pdf_file: '', tex_file: '' }),
                  }),
                100
              )
            )
        );

      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => screen.getByText('openai'));
      await setupFilledForm();

      const button = screen.getByRole('button', { name: /Tailor Resume with AI/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Tailoring Resume/i)).toBeInTheDocument();
      });
    });

    it('handles upload error', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ openai: true }),
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ error: 'Upload failed' }),
        });

      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => screen.getByText('openai'));
      await setupFilledForm();

      const button = screen.getByRole('button', { name: /Tailor Resume with AI/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Failed to upload resume/i)).toBeInTheDocument();
      });
    });

    it('handles tailor error', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ openai: true }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ file_path: 'uploads/resume.pdf' }),
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ error: 'AI error' }),
        });

      render(<TailorForm onComplete={mockOnComplete} />);

      await waitFor(() => screen.getByText('openai'));
      await setupFilledForm();

      const button = screen.getByRole('button', { name: /Tailor Resume with AI/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Failed to tailor resume/i)).toBeInTheDocument();
      });
    });
  });
});
