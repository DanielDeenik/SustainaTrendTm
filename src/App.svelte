<script lang="ts">
  import "./app.css";
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import Navigation from './lib/components/Navigation.svelte';
  import ErrorBoundary from './lib/components/ErrorBoundary.svelte';
  import { apiRequest } from '$lib/api/client';

  let metrics = [];
  let loading = true;
  let error = null;

  async function fetchMetrics() {
    try {
      loading = true;
      error = null;
      metrics = await apiRequest('/api/metrics');
    } catch (err) {
      error = err instanceof Error ? err : new Error('Failed to load metrics');
      console.error('Failed to load metrics:', error);
    } finally {
      loading = false;
    }
  }

  onMount(fetchMetrics);
</script>

<div class="min-h-screen bg-white dark:bg-gray-900">
  <Navigation />

  <main class="max-w-7xl mx-auto px-4 py-8">
    <ErrorBoundary>
      {#if loading}
        <div class="flex justify-center items-center min-h-[200px]">
          <div class="spinner"></div>
        </div>
      {:else if error}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p class="font-bold">Error loading data</p>
          <p>{error.message}</p>
          <button 
            class="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            on:click={fetchMetrics}
          >
            Try Again
          </button>
        </div>
      {:else}
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each metrics as metric}
            <div class="bg-white rounded-lg shadow p-6">
              <div class="flex justify-between items-start mb-4">
                <h3 class="text-lg font-semibold">{metric.name}</h3>
                <span class="px-2 py-1 rounded-full text-sm capitalize
                  {metric.category === 'emissions' ? 'bg-red-100 text-red-800' :
                   metric.category === 'water' ? 'bg-blue-100 text-blue-800' :
                   'bg-green-100 text-green-800'}">
                  {metric.category}
                </span>
              </div>
              <p class="text-3xl font-bold text-green-600">
                {metric.value} {metric.unit}
              </p>
              <p class="text-sm text-gray-500 mt-2">
                Last updated: {new Date(metric.timestamp).toLocaleString()}
              </p>
            </div>
          {/each}
        </div>
      {/if}
    </ErrorBoundary>
  </main>

  <footer class="border-t border-gray-200 dark:border-gray-800 mt-auto">
    <div class="max-w-7xl mx-auto px-4 py-4 text-center text-gray-600 dark:text-gray-400">
      © {new Date().getFullYear()} Sustainability Intelligence Platform
    </div>
  </footer>
</div>

<style>
  .spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #22c55e;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style>