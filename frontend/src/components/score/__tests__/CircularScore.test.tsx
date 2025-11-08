import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import CircularScore from '../CircularScore';

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    circle: ({ children, ...props }: any) => <circle {...props}>{children}</circle>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
  },
}));

describe('CircularScore', () => {
  it('should render score with label', () => {
    render(<CircularScore score={85} label="Test Score" />);
    
    expect(screen.getByText('85')).toBeInTheDocument();
    expect(screen.getByText('Test Score')).toBeInTheDocument();
  });

  it('should show percentage symbol when showPercentage is true', () => {
    render(<CircularScore score={75} label="Test" showPercentage={true} />);
    
    expect(screen.getByText('%')).toBeInTheDocument();
  });

  it('should not show percentage symbol when showPercentage is false', () => {
    render(<CircularScore score={75} label="Test" showPercentage={false} />);
    
    expect(screen.queryByText('%')).not.toBeInTheDocument();
  });

  it('should render different sizes', () => {
    const { rerender } = render(<CircularScore score={80} label="Small" size="sm" />);
    expect(screen.getByText('Small')).toBeInTheDocument();

    rerender(<CircularScore score={80} label="Medium" size="md" />);
    expect(screen.getByText('Medium')).toBeInTheDocument();

    rerender(<CircularScore score={80} label="Large" size="lg" />);
    expect(screen.getByText('Large')).toBeInTheDocument();
  });

  it('should round decimal scores', () => {
    render(<CircularScore score={87.6} label="Test" />);
    
    expect(screen.getByText('88')).toBeInTheDocument();
  });

  it('should apply correct color class based on score', () => {
    const { rerender, container } = render(<CircularScore score={90} label="Excellent" />);
    expect(container.querySelector('.text-green-600')).toBeInTheDocument();

    rerender(<CircularScore score={70} label="Good" />);
    expect(container.querySelector('.text-blue-600')).toBeInTheDocument();

    rerender(<CircularScore score={50} label="Fair" />);
    expect(container.querySelector('.text-yellow-600')).toBeInTheDocument();

    rerender(<CircularScore score={30} label="Poor" />);
    expect(container.querySelector('.text-red-600')).toBeInTheDocument();
  });
});
