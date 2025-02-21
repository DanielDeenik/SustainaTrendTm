<script lang="ts">
  import { fade } from 'svelte/transition';
  import { onMount } from 'svelte';
  import type { Metric } from '$lib/types/schema';

  let metrics: Metric[] = [];
  let loading = true;

  onMount(async () => {
    try {
      const response = await fetch('/api/metrics');
      metrics = await response.json();
    } catch (error) {
      console.error('Error fetching metrics:', error);
    } finally {
      loading = false;
    }
  });

  // Group metrics by category
  $: metricsByCategory = metrics.reduce((acc, metric) => {
    if (!acc[metric.category]) {
      acc[metric.category] = [];
    }
    acc[metric.category].push(metric);
    return acc;
  }, {} as Record<string, Metric[]>);
</script>

<div class="min-h-screen bg-gray-50 dark:bg-gray-900" in:fade>
  <!-- Header -->
  <header class="bg-white dark:bg-gray-800 shadow">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Sustainability Dashboard
      </h1>
    </div>
  </header>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    {#if loading}
      <div class="flex justify-center items-center h-64">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    {:else}
      <!-- Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each Object.entries(metricsByCategory) as [category, categoryMetrics]}
          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white capitalize">
                {category}
              </h3>
              <div class="mt-4 space-y-4">
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
          </div>
        {/each}
      </div>
    {/if}
  </main>
</div>