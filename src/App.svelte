<script lang="ts">
  import "./app.css";
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { LineChart } from "@carbon/charts-svelte";
  import Badge from '$lib/components/ui/Badge.svelte';
  import { apiRequest } from '$lib/api/client';
  import type { APIError } from '$lib/api/client';
  import type { Metric } from '$lib/types/schema';

  let metrics: Metric[] = [];
  let loading = true;
  let error: Error | APIError | null = null;

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

  // Prepare chart data
  $: chartData = metrics.map(m => ({
    group: m.category,
    date: new Date(m.timestamp),
    value: m.value
  }));

  $: chartOptions = {
    title: 'Sustainability Metrics',
    axes: {
      bottom: {
        title: 'Time',
        mapsTo: 'date',
        scaleType: 'time'
      },
      left: {
        mapsTo: 'value',
        scaleType: 'linear'
      }
    },
    height: '400px',
    toolbar: {
      enabled: false
    }
  };
</script>

<div class="min-h-screen bg-white dark:bg-gray-900">
  <header class="bg-white shadow dark:bg-gray-800">
    <div class="max-w-7xl mx-auto py-6 px-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Sustainability Intelligence
      </h1>
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
      <!-- Chart Section -->
      {#if metrics.length > 0}
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <LineChart data={chartData} options={chartOptions} />
        </div>
      {/if}

      <!-- Metrics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each metrics as metric (metric.id)}
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div class="flex justify-between items-start">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {metric.name}
              </h3>
              <Badge variant={metric.category === 'emissions' ? 'error' : 'default'}>
                {metric.category}
              </Badge>
            </div>
            <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-4">
              {metric.value} {metric.unit}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
              Last updated: {new Date(metric.timestamp).toLocaleString()}
            </p>
          </div>
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