<script lang="ts">
  import "./app.css";
  import Navigation from '$lib/components/Navigation.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Loading from '$lib/components/ui/Loading.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import { onMount } from 'svelte';
  import { logger } from '$lib/services/logger';

  let metrics = [];
  let loading = true;
  let error: Error | null = null;

  async function fetchLatestMetrics() {
    try {
      loading = true;
      error = null;
      const response = await fetch('http://0.0.0.0:8000/api/metrics');
      if (!response.ok) throw new Error('Failed to fetch metrics');
      metrics = await response.json();
      console.log('Fetched metrics:', metrics);
    } catch (err) {
      console.error('Error:', err);
      error = err instanceof Error ? err : new Error('Failed to load metrics');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    logger.info('App mounted, fetching metrics');
    fetchLatestMetrics();
  });
</script>

<div class="min-h-screen bg-white dark:bg-gray-900">
  <Navigation />

  <main class="max-w-7xl mx-auto px-4 py-8">
    <div class="space-y-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Sustainability Intelligence Dashboard
      </h1>

      {#if loading}
        <div class="flex justify-center items-center min-h-[200px]">
          <Loading size="lg" />
        </div>
      {:else if error}
        <Alert variant="error">
          <div class="flex flex-col gap-2">
            <strong class="font-bold">Error!</strong>
            <p class="block sm:inline"> {error.message}</p>
            <button 
              class="mt-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
              on:click={fetchLatestMetrics}
            >
              Try Again
            </button>
          </div>
        </Alert>
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
  </main>

  <footer class="border-t border-gray-200 dark:border-gray-800 mt-auto">
    <div class="max-w-7xl mx-auto px-4 py-4 text-center text-gray-600 dark:text-gray-400">
      © {new Date().getFullYear()} Sustainability Intelligence Platform
    </div>
  </footer>
</div>