<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import type { Metric } from '$lib/types/schema';
  import { apiRequest } from '$lib/api/client';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Loading from '$lib/components/ui/Loading.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';

  let metrics: Metric[] = [];
  let loading = true;
  let error: Error | null = null;
  let selectedCategory: string | null = null;

  async function fetchMetrics(category?: string) {
    try {
      loading = true;
      const endpoint = category 
        ? `/api/metrics?category=${encodeURIComponent(category)}`
        : '/api/metrics';
      metrics = await apiRequest<Metric[]>(endpoint);
      error = null;
    } catch (err) {
      console.error('Error fetching metrics:', err);
      error = err instanceof Error ? err : new Error('Failed to load metrics');
    } finally {
      loading = false;
    }
  }

  onMount(() => fetchMetrics());

  const categories = ['emissions', 'water', 'energy', 'waste', 'social', 'governance'];

  function filterMetrics(category: string | null) {
    selectedCategory = category;
    fetchMetrics(category ?? undefined);
  }
</script>

<div class="space-y-6" in:fade>
  <div class="flex justify-between items-center">
    <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
      Sustainability Metrics
    </h2>
    <div class="flex gap-2">
      <button
        class="px-4 py-2 rounded-lg {!selectedCategory ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'}"
        on:click={() => filterMetrics(null)}
      >
        All
      </button>
      {#each categories as category}
        <button
          class="px-4 py-2 rounded-lg {selectedCategory === category ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'}"
          on:click={() => filterMetrics(category)}
        >
          {category}
        </button>
      {/each}
    </div>
  </div>

  {#if loading}
    <Loading size="lg" />
  {:else if error}
    <Alert variant="error">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline ml-2">{error.message}</span>
      <button
        class="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        on:click={() => fetchMetrics(selectedCategory ?? undefined)}
      >
        Retry
      </button>
    </Alert>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {#each metrics as metric}
        <Card 
          title={metric.name}
          subtitle={metric.category}
        >
          <div class="flex justify-between items-start">
            <Badge variant={metric.category === 'emissions' ? 'error' : 'default'}>
              {metric.category}
            </Badge>
            <span class="text-2xl font-bold text-primary">
              {metric.value} {metric.unit}
            </span>
          </div>
          {#if metric.metric_metadata}
            <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Additional Information
              </h4>
              <div class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
                {#each Object.entries(metric.metric_metadata) as [key, value]}
                  <p class="capitalize">{key}: {value}</p>
                {/each}
              </div>
            </div>
          {/if}
        </Card>
      {/each}
    </div>
  {/if}
</div>