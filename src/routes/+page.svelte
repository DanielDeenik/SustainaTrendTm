<script lang="ts">
  import { onMount } from 'svelte';
  import type { Metric } from '$lib/types/schema';
  import { apiRequest } from '$lib/api/client';
  import { fade } from 'svelte/transition';

  let metrics: Metric[] = [];
  let loading = true;
  let error: Error | null = null;

  async function fetchMetrics() {
    try {
      loading = true;
      metrics = await apiRequest<Metric[]>('/api/metrics');
      error = null;
    } catch (err) {
      console.error('Error fetching metrics:', err);
      error = err instanceof Error ? err : new Error('Failed to load metrics');
    } finally {
      loading = false;
    }
  }

  onMount(fetchMetrics);

  $: metricsByCategory = metrics.reduce((acc, metric) => {
    if (!acc[metric.category]) {
      acc[metric.category] = [];
    }
    acc[metric.category].push(metric);
    return acc;
  }, {} as Record<string, Metric[]>);
</script>

<div class="space-y-6" in:fade>
  <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
    Sustainability Metrics Dashboard
  </h2>

  {#if loading}
    <div class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline ml-2">{error.message}</span>
      <button
        class="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        on:click={fetchMetrics}
      >
        Retry
      </button>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each Object.entries(metricsByCategory) as [category, categoryMetrics]}
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white capitalize mb-4">
            {category}
          </h3>
          <div class="space-y-4">
            {#each categoryMetrics as metric}
              <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
                <p class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {metric.name}
                </p>
                <p class="mt-1 text-2xl font-semibold text-primary">
                  {metric.value} {metric.unit}
                </p>
                {#if metric.metric_metadata}
                  <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    {#each Object.entries(metric.metric_metadata) as [key, value]}
                      <p class="capitalize">{key}: {value}</p>
                    {/each}
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>