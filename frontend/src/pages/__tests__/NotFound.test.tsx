import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import NotFound from '../NotFound';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('NotFound Page', () => {
  it('should render 404 message', () => {
    renderWithRouter(<NotFound />);
    
    expect(screen.getByText(/404 - Page Not Found/i)).toBeInTheDocument();
  });

  it('should display helpful message', () => {
    renderWithRouter(<NotFound />);
    
    expect(screen.getByText(/The page you're looking for doesn't exist/i)).toBeInTheDocument();
  });

  it('should have a go home button', () => {
    renderWithRouter(<NotFound />);
    
    expect(screen.getByRole('button', { name: /go home/i })).toBeInTheDocument();
  });
});
