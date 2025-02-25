<script lang="ts">
  import "./app.css";
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import MetricCard from '$lib/components/sustainability/MetricCard.svelte';
  import { apiRequest } from '$lib/api/client';
  import type { APIError } from '$lib/api/client';
  import type { Metric } from '$lib/types/schema';

  let metrics: Metric[] = [];
  let loading = true;
  let error: Error | APIError | null = null;
  let aiEnabled = false;

  // Group metrics by name for historical data
  $: metricsByName = metrics.reduce((acc, metric) => {
    const name = metric.name;
    if (!acc[name]) acc[name] = [];
    acc[name].push(metric);
    acc[name].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    return acc;
  }, {} as Record<string, Metric[]>);

  // Get unique latest metrics
  $: latestMetrics = Object.values(metricsByName).map(group => group[group.length - 1]);

  async function fetchData() {
    try {
      loading = true;
      error = null;
      metrics = await apiRequest('/api/metrics');
    } catch (err) {
      error = err instanceof Error ? err : new Error('Failed to load data');
      console.error('Failed to load data:', error);
    } finally {
      loading = false;
    }
  }

  onMount(fetchData);
</script>

<div class="min-h-screen bg-white dark:bg-gray-900">
  <header class="bg-white shadow dark:bg-gray-800">
    <div class="max-w-7xl mx-auto py-6 px-4">
      <div class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Sustainability Intelligence
        </h1>
        <button
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          class:opacity-50={loading}
          disabled={loading}
          on:click={() => aiEnabled = !aiEnabled}
        >
          {aiEnabled ? 'Disable AI' : 'Enable AI'}
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-4 py-8" in:fade>
    {#if loading}
      <div class="flex justify-center items-center min-h-[200px]">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    {:else if error}
      <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
        <strong class="font-bold">Error!</strong>
        <p class="block sm:inline">{error.message}</p>
        <button
          class="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition-colors"
          on:click={fetchData}
        >
          Try Again
        </button>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each latestMetrics as metric (metric.id)}
          <MetricCard 
            {metric}
            historicalMetrics={metricsByName[metric.name].slice(0, -1)}
            {aiEnabled} 
          />
        {/each}
      </div>
    {/if}
  </main>
</div>

<style>
  :global(body) {
    margin: 0;
    font-family: system-ui, -apple-system, sans-serif;
  }
</style>