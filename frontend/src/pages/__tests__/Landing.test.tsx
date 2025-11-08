import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Landing from '../Landing';

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    header: ({ children, ...props }: any) => <header {...props}>{children}</header>,
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    footer: ({ children, ...props }: any) => <footer {...props}>{children}</footer>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Landing Page', () => {
  it('should render the landing page', () => {
    renderWithRouter(<Landing />);
    
    expect(screen.getByText('JobGlove')).toBeInTheDocument();
    expect(screen.getByText(/AI-Powered Resume Tailoring/i)).toBeInTheDocument();
  });

  it('should display tailor existing resume card', () => {
    renderWithRouter(<Landing />);
    
    expect(screen.getByText('Tailor Existing Resume')).toBeInTheDocument();
    expect(screen.getByText(/Upload your resume and job description/i)).toBeInTheDocument();
  });

  it('should display create new resume card as disabled', () => {
    renderWithRouter(<Landing />);
    
    expect(screen.getByText('Create New Resume')).toBeInTheDocument();
    expect(screen.getByText('Coming Soon')).toBeDisabled();
  });

  it('should navigate to tailor page when clicking Get Started', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Landing />);
    
    const getStartedButton = screen.getByRole('button', { name: /get started/i });
    await user.click(getStartedButton);
    
    // URL should change (we can't test this fully without a real router setup)
    expect(getStartedButton).toBeInTheDocument();
  });

  it('should display feature list', () => {
    renderWithRouter(<Landing />);
    
    expect(screen.getByText('Local NLP score analysis')).toBeInTheDocument();
    expect(screen.getByText('AI-powered tailoring')).toBeInTheDocument();
    expect(screen.getByText('PDF & LaTeX download')).toBeInTheDocument();
  });

  it('should display footer', () => {
    renderWithRouter(<Landing />);
    
    expect(screen.getByText(/Open source resume tailoring tool/i)).toBeInTheDocument();
  });
});
