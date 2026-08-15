import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Header } from './Header';

describe('Header', () => {
  it('renders title, prototype notice, and run button', () => {
    const onRun = vi.fn();
    render(<Header isLoading={false} hasRun={false} onRunAnalysis={onRun} />);

    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('VeriClaim');
    expect(screen.getByText(/Demonstration Prototype:/i)).toBeInTheDocument();
    const button = screen.getByRole('button', { name: /Run analysis/i });
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(onRun).toHaveBeenCalledTimes(1);
  });

  it('renders busy state and disables button while loading', () => {
    const onRun = vi.fn();
    render(<Header isLoading={true} hasRun={false} onRunAnalysis={onRun} />);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(button).toHaveTextContent(/Running analysis.../i);
  });

  it('renders "Run analysis again" when hasRun is true', () => {
    const onRun = vi.fn();
    render(<Header isLoading={false} hasRun={true} onRunAnalysis={onRun} />);

    expect(screen.getByRole('button', { name: /Run analysis again/i })).toBeInTheDocument();
  });
});
