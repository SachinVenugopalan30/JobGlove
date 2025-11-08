import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Tailor from '../Tailor';

// Mock StepIndicator component
vi.mock('@/components/tailor/StepIndicator', () => ({
  default: ({ steps, currentStep }: any) => (
    <div data-testid="step-indicator">
      {steps.map((step: any) => (
        <div key={step.number}>{step.label}</div>
      ))}
    </div>
  ),
}));

// Mock UploadStep component
vi.mock('@/components/tailor/UploadStep', () => ({
  default: ({ onComplete }: any) => (
    <div data-testid="upload-step">Upload Step</div>
  ),
}));

// Mock lucide-react with proper function components
vi.mock('lucide-react', () => ({
  ArrowLeft: (props: any) => <svg data-testid="arrow-left" {...props} />,
  Upload: (props: any) => <svg data-testid="upload-icon" {...props} />,
  FileText: (props: any) => <svg data-testid="file-icon" {...props} />,
  CheckCircle: (props: any) => <svg data-testid="check-circle-icon" {...props} />,
  AlertCircle: (props: any) => <svg data-testid="alert-icon" {...props} />,
  X: (props: any) => <svg data-testid="x-icon" {...props} />,
  Check: (props: any) => <svg data-testid="check-icon" {...props} />,
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    header: ({ children, ...props }: any) => <header {...props}>{children}</header>,
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Tailor Page', () => {
  it('should render the tailor page', () => {
    renderWithRouter(<Tailor />);
    
    expect(screen.getByText('Upload')).toBeInTheDocument();
  });

  it('should display back button', () => {
    renderWithRouter(<Tailor />);
    
    expect(screen.getByRole('button', { name: /back/i })).toBeInTheDocument();
  });

  it('should display step indicator', () => {
    renderWithRouter(<Tailor />);
    
    expect(screen.getByText('Upload')).toBeInTheDocument();
    expect(screen.getByText('Analyze')).toBeInTheDocument();
    expect(screen.getByText('Tailor')).toBeInTheDocument();
    expect(screen.getByText('Download')).toBeInTheDocument();
  });

  it('should handle back button click', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Tailor />);
    
    const backButton = screen.getByRole('button', { name: /back/i });
    await user.click(backButton);
    
    expect(backButton).toBeInTheDocument();
  });
});
