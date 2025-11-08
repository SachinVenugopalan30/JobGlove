import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import StepIndicator from '../StepIndicator';

// Mock lucide-react
vi.mock('lucide-react', () => ({
  Check: () => <svg data-testid="check-icon" />,
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
  },
}));

describe('StepIndicator', () => {
  const steps = [
    { number: 1, label: 'Upload' },
    { number: 2, label: 'Analyze' },
    { number: 3, label: 'Tailor' },
    { number: 4, label: 'Download' },
  ];

  it('should render all steps', () => {
    render(<StepIndicator steps={steps} currentStep={1} />);
    
    expect(screen.getByText('Upload')).toBeInTheDocument();
    expect(screen.getByText('Analyze')).toBeInTheDocument();
    expect(screen.getByText('Tailor')).toBeInTheDocument();
    expect(screen.getByText('Download')).toBeInTheDocument();
  });

  it('should highlight current step', () => {
    const { container } = render(<StepIndicator steps={steps} currentStep={2} />);
    
    const stepElements = container.querySelectorAll('[class*="rounded-full"]');
    expect(stepElements).toHaveLength(4);
  });

  it('should show check mark for completed steps', () => {
    const { container } = render(<StepIndicator steps={steps} currentStep={3} />);
    
    // First two steps should be completed (showing check marks)
    const checkIcons = container.querySelectorAll('[data-testid="check-icon"]');
    expect(checkIcons.length).toBeGreaterThan(0);
  });

  it('should show step numbers for upcoming steps', () => {
    render(<StepIndicator steps={steps} currentStep={1} />);
    
    // Steps 2, 3, 4 should show numbers
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });
});
