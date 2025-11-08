import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import Recommendations from '../Recommendations';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    li: ({ children, ...props }: any) => <li {...props}>{children}</li>,
  },
}));

// Mock lucide-react
vi.mock('lucide-react', () => ({
  Lightbulb: (props: any) => <svg data-testid="lightbulb" {...props} />,
  TrendingUp: (props: any) => <svg data-testid="trending-up" {...props} />,
  AlertTriangle: (props: any) => <svg data-testid="alert-triangle" {...props} />,
}));

describe('Recommendations', () => {
  it('should render recommendations', () => {
    const recommendations = [
      'Add more quantified achievements',
      'Include relevant keywords from the job description',
      'Improve formatting consistency',
    ];
    
    render(<Recommendations recommendations={recommendations} />);
    
    expect(screen.getByText('Recommendations')).toBeInTheDocument();
    expect(screen.getByText('Add more quantified achievements')).toBeInTheDocument();
    expect(screen.getByText('Include relevant keywords from the job description')).toBeInTheDocument();
    expect(screen.getByText('Improve formatting consistency')).toBeInTheDocument();
  });

  it('should not render when recommendations is empty', () => {
    const { container } = render(<Recommendations recommendations={[]} />);
    
    expect(container.firstChild).toBeNull();
  });

  it('should not render when recommendations is undefined', () => {
    const { container } = render(<Recommendations recommendations={undefined as any} />);
    
    expect(container.firstChild).toBeNull();
  });

  it('should display icons for recommendations', () => {
    const recommendations = [
      'First recommendation',
      'Second recommendation',
      'Third recommendation',
    ];
    
    render(<Recommendations recommendations={recommendations} />);
    
    // Should have at least one icon
    const icons = screen.queryAllByTestId(/lightbulb|trending-up|alert-triangle/);
    expect(icons.length).toBeGreaterThan(0);
  });

  it('should render multiple recommendations', () => {
    const recommendations = ['Rec 1', 'Rec 2', 'Rec 3', 'Rec 4', 'Rec 5'];
    
    render(<Recommendations recommendations={recommendations} />);
    
    recommendations.forEach(rec => {
      expect(screen.getByText(rec)).toBeInTheDocument();
    });
  });
});
