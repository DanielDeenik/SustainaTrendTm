<script lang="ts">
  import { fade } from 'svelte/transition';
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Loading from '$lib/components/ui/Loading.svelte';
  import { onMount } from 'svelte';
  import { apiRequest } from '$lib/api/client';
  import type { Metric } from '$lib/types/schema';
  import { logger } from '$lib/services/logger';
  import { config } from '$lib/config';

  let metrics: Metric[] = [];
  let loading = true;
  let error: Error | null = null;

  async function fetchLatestMetrics() {
    try {
      loading = true;
      error = null;
      logger.info('Starting to fetch metrics from API', { endpoint: config.api.metrics });
      console.log('Fetching metrics from:', config.apiUrl + '/api/metrics'); // Debug log

      metrics = await apiRequest<Metric[]>('/api/metrics');

      console.log('Received metrics:', metrics); // Debug log
      logger.info('Dashboard metrics loaded successfully', { 
        count: metrics.length,
        categories: metrics.map(m => m.category)
      });
    } catch (err) {
      console.error('Failed to fetch metrics:', err); // Debug log
      error = err instanceof Error ? err : new Error('Failed to load metrics');
      logger.error('Failed to load dashboard metrics', error);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    logger.info('Dashboard component mounted');
    fetchLatestMetrics();
  });
</script>

<div class="space-y-6" in:fade>
  <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-8">
    Sustainability Intelligence Dashboard
  </h1>

  {#if loading}
    <div class="flex justify-center items-center min-h-[200px]">
      <Loading size="lg" />
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
      <strong class="font-bold">Error!</strong>
      <p class="block sm:inline"> {error.message}</p>
      <button 
        class="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        on:click={fetchLatestMetrics}
      >
        Try Again
      </button>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Carbon Emissions Card -->
      <Card title="Environmental Impact">
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-gray-600 dark:text-gray-400">Carbon Emissions</span>
            <Badge variant="error">Critical</Badge>
          </div>
          {#if metrics.find(m => m.category === 'emissions')}
            {@const emission = metrics.find(m => m.category === 'emissions')}
            <p class="text-2xl font-bold text-primary">{emission.value} {emission.unit}</p>
            <p class="text-sm text-gray-500">Latest measurement</p>
          {:else}
            <p class="text-2xl font-bold text-gray-400">No Data</p>
          {/if}
        </div>
      </Card>

      <!-- Water Usage Card -->
      <Card title="Water Usage">
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-gray-600 dark:text-gray-400">Consumption Rate</span>
            <Badge variant="warning">Moderate</Badge>
          </div>
          {#if metrics.find(m => m.category === 'water')}
            {@const water = metrics.find(m => m.category === 'water')}
            <p class="text-2xl font-bold text-primary">{water.value} {water.unit}</p>
            <p class="text-sm text-gray-500">Latest measurement</p>
          {:else}
            <p class="text-2xl font-bold text-gray-400">No Data</p>
          {/if}
        </div>
      </Card>

      <!-- Energy Efficiency Card -->
      <Card title="Energy Efficiency">
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-gray-600 dark:text-gray-400">Power Usage</span>
            <Badge variant="success">Optimal</Badge>
          </div>
          {#if metrics.find(m => m.category === 'energy')}
            {@const energy = metrics.find(m => m.category === 'energy')}
            <p class="text-2xl font-bold text-primary">{energy.value} {energy.unit}</p>
            <p class="text-sm text-gray-500">Latest measurement</p>
          {:else}
            <p class="text-2xl font-bold text-gray-400">No Data</p>
          {/if}
        </div>
      </Card>
    </div>
  {/if}
</div>