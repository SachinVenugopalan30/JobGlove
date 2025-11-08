import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import KeywordBadges from '../KeywordBadges';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

// Mock lucide-react
vi.mock('lucide-react', () => ({
  CheckCircle: (props: any) => <svg data-testid="check-circle" {...props} />,
  XCircle: (props: any) => <svg data-testid="x-circle" {...props} />,
}));

describe('KeywordBadges', () => {
  it('should render matched keywords', () => {
    const matched = ['React', 'TypeScript', 'Node.js'];
    const missing: string[] = [];
    
    render(<KeywordBadges matched={matched} missing={missing} />);
    
    expect(screen.getByText('Matched Keywords (3)')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('Node.js')).toBeInTheDocument();
  });

  it('should render missing keywords', () => {
    const matched: string[] = [];
    const missing = ['Docker', 'Kubernetes', 'AWS'];
    
    render(<KeywordBadges matched={matched} missing={missing} />);
    
    expect(screen.getByText('Missing Keywords (3)')).toBeInTheDocument();
    expect(screen.getByText('Docker')).toBeInTheDocument();
    expect(screen.getByText('Kubernetes')).toBeInTheDocument();
    expect(screen.getByText('AWS')).toBeInTheDocument();
  });

  it('should render both matched and missing keywords', () => {
    const matched = ['React', 'TypeScript'];
    const missing = ['Docker', 'AWS'];
    
    render(<KeywordBadges matched={matched} missing={missing} />);
    
    expect(screen.getByText('Matched Keywords (2)')).toBeInTheDocument();
    expect(screen.getByText('Missing Keywords (2)')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Docker')).toBeInTheDocument();
  });

  it('should show message when no keywords are available', () => {
    render(<KeywordBadges matched={[]} missing={[]} />);
    
    expect(screen.getByText('No keyword analysis available')).toBeInTheDocument();
  });

  it('should display check and x icons', () => {
    const matched = ['React'];
    const missing = ['Docker'];
    
    render(<KeywordBadges matched={matched} missing={missing} />);
    
    expect(screen.getByTestId('check-circle')).toBeInTheDocument();
    expect(screen.getByTestId('x-circle')).toBeInTheDocument();
  });
});
