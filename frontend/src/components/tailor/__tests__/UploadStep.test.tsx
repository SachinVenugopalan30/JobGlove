import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import UploadStep from '../UploadStep';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock API client
vi.mock('@/lib/api', () => ({
  ApiClient: {
    uploadResume: vi.fn(),
  },
}));

import { ApiClient } from '@/lib/api';

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('UploadStep', () => {
  const mockOnComplete = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render upload step with title and description', () => {
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    expect(screen.getByText('Upload Your Resume')).toBeInTheDocument();
    expect(screen.getByText(/Upload your resume and paste the job description/i)).toBeInTheDocument();
  });

  it('should display file upload area', () => {
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    expect(screen.getByText(/Drag & drop your resume/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument();
  });

  it('should display job description textarea', () => {
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    expect(screen.getByPlaceholderText('Paste the job description here...')).toBeInTheDocument();
  });

  it('should validate file type', async () => {
    render(<UploadStep onComplete={mockOnComplete} />);

    const invalidFile = new File(['content'], 'test.txt', { type: 'text/plain' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    // Use fireEvent.change instead of user.upload to properly trigger validation
    Object.defineProperty(input, 'files', {
      value: [invalidFile],
      writable: false,
    });
    fireEvent.change(input);

    expect(await screen.findByText(/Please upload a PDF or Word document/i)).toBeInTheDocument();
  });  it('should validate file size', async () => {
    const user = userEvent.setup();
    render(<UploadStep onComplete={mockOnComplete} />);

    // Create a file larger than 5MB
    const largeFile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    await user.upload(input, largeFile);

    expect(await screen.findByText(/File size must be less than 5MB/i)).toBeInTheDocument();
  });

  it('should accept valid PDF file', async () => {
    const user = userEvent.setup();
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    const validFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    await user.upload(input, validFile);
    
    await waitFor(() => {
      expect(screen.getByText('resume.pdf')).toBeInTheDocument();
    });
  });

  it('should allow removing uploaded file', async () => {
    const user = userEvent.setup();
    render(<UploadStep onComplete={mockOnComplete} />);
    
    const validFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    await user.upload(input, validFile);
    
    await waitFor(() => {
      expect(screen.getByText('resume.pdf')).toBeInTheDocument();
    });

    const removeButton = screen.getByRole('button', { name: '' });
    await user.click(removeButton);
    
    await waitFor(() => {
      expect(screen.queryByText('resume.pdf')).not.toBeInTheDocument();
    });
  });

  it('should update job description character count', async () => {
    const user = userEvent.setup();
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    const textarea = screen.getByPlaceholderText('Paste the job description here...');
    await user.type(textarea, 'Test job description');
    
    expect(screen.getByText(/20 characters/i)).toBeInTheDocument();
  });

  it('should disable submit button when file or job description is missing', () => {
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    const submitButton = screen.getByRole('button', { name: /Analyze Resume/i });
    expect(submitButton).toBeDisabled();
  });

  it('should enable submit button when both file and job description are provided', async () => {
    const user = userEvent.setup();
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    // Upload file
    const validFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, validFile);
    
    // Type job description
    const textarea = screen.getByPlaceholderText('Paste the job description here...');
    await user.type(textarea, 'Job description here');
    
    await waitFor(() => {
      const submitButton = screen.getByRole('button', { name: /Analyze Resume/i });
      expect(submitButton).not.toBeDisabled();
    });
  });

  it('should call API and onComplete when submitting', async () => {
    const user = userEvent.setup();
    const mockUploadResponse = { file_path: 'uploads/resume.pdf', filename: 'resume.pdf' };
    (ApiClient.uploadResume as any).mockResolvedValueOnce(mockUploadResponse);
    
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    // Upload file
    const validFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, validFile);
    
    // Type job description
    const textarea = screen.getByPlaceholderText('Paste the job description here...');
    const jobDesc = 'Software Engineer position';
    await user.type(textarea, jobDesc);
    
    // Submit
    const submitButton = screen.getByRole('button', { name: /Analyze Resume/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(ApiClient.uploadResume).toHaveBeenCalledWith(validFile);
    });

    // Wait for success animation and callback
    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalledWith('uploads/resume.pdf', jobDesc);
    }, { timeout: 2000 });
  });

  it('should show error message when upload fails', async () => {
    const user = userEvent.setup();
    (ApiClient.uploadResume as any).mockRejectedValueOnce(new Error('Upload failed'));
    
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    // Upload file
    const validFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, validFile);
    
    // Type job description
    const textarea = screen.getByPlaceholderText('Paste the job description here...');
    await user.type(textarea, 'Job description');
    
    // Submit
    const submitButton = screen.getByRole('button', { name: /Analyze Resume/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Upload failed/i)).toBeInTheDocument();
    });
  });

  it('should show loading state during upload', async () => {
    const user = userEvent.setup();
    let resolveUpload: any;
    (ApiClient.uploadResume as any).mockImplementationOnce(() => 
      new Promise(resolve => { resolveUpload = resolve; })
    );
    
    renderWithRouter(<UploadStep onComplete={mockOnComplete} />);
    
    // Upload file
    const validFile = new File(['content'], 'resume.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, validFile);
    
    // Type job description
    const textarea = screen.getByPlaceholderText('Paste the job description here...');
    await user.type(textarea, 'Job description');
    
    // Submit
    const submitButton = screen.getByRole('button', { name: /Analyze Resume/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Uploading.../i)).toBeInTheDocument();
    });

    // Resolve upload
    resolveUpload({ file_path: 'uploads/resume.pdf', filename: 'resume.pdf' });
  });
});
