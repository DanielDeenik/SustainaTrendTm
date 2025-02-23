import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import Dashboard from '../routes/+page.svelte';
import { apiRequest } from '$lib/api/client';

// Mock the API request
vi.mock('$lib/api/client', () => ({
  apiRequest: vi.fn()
}));

describe('Dashboard Component', () => {
  const mockMetrics = [
    {
      id: 1,
      name: 'Carbon Footprint',
      category: 'emissions',
      value: 156.7,
      unit: 'kg CO2e',
      timestamp: '2025-02-23T18:54:08.466573'
    },
    {
      id: 2,
      name: 'Water Consumption',
      category: 'water',
      value: 2450.5,
      unit: 'gallons',
      timestamp: '2025-02-23T18:54:08.466573'
    }
  ];

  it('should display loading state initially', () => {
    render(Dashboard);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('should display metrics when data is loaded', async () => {
    vi.mocked(apiRequest).mockResolvedValue(mockMetrics);
    render(Dashboard);
    
    // Wait for metrics to load
    await screen.findByText('Carbon Footprint');
    
    expect(screen.getByText('156.7 kg CO2e')).toBeInTheDocument();
    expect(screen.getByText('2450.5 gallons')).toBeInTheDocument();
  });

  it('should handle errors appropriately', async () => {
    const error = new Error('Failed to fetch metrics');
    vi.mocked(apiRequest).mockRejectedValue(error);
    render(Dashboard);
    
    await screen.findByText(/Error loading dashboard data/i);
    expect(screen.getByText('Failed to fetch metrics')).toBeInTheDocument();
  });
});
