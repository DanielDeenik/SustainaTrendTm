import { writable } from 'svelte/store';
import type { SustainabilityMetrics } from '../types/sustainability';

// Create stores for sustainability data
export const sustainabilityMetrics = writable<SustainabilityMetrics[]>([]);
export const isLoading = writable<boolean>(false);
export const error = writable<string | null>(null);

// Fetch sustainability metrics
export async function fetchSustainabilityMetrics(companyId: string) {
  isLoading.set(true);
  error.set(null);
  
  try {
    const response = await fetch(`/api/sustainability/${companyId}`);
    if (!response.ok) throw new Error('Failed to fetch sustainability metrics');
    
    const data = await response.json();
    sustainabilityMetrics.set(data);
  } catch (err) {
    error.set(err.message);
    console.error('Error fetching sustainability metrics:', err);
  } finally {
    isLoading.set(false);
  }
}

// Update sustainability metrics
export async function updateSustainabilityMetrics(metrics: Omit<SustainabilityMetrics, 'id'>) {
  isLoading.set(true);
  error.set(null);
  
  try {
    const response = await fetch('/api/sustainability', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metrics),
    });
    
    if (!response.ok) throw new Error('Failed to update sustainability metrics');
    
    const updatedData = await response.json();
    sustainabilityMetrics.update(current => 
      current.map(item => 
        item.companyId === metrics.companyId ? updatedData : item
      )
    );
  } catch (err) {
    error.set(err.message);
    console.error('Error updating sustainability metrics:', err);
  } finally {
    isLoading.set(false);
  }
}
