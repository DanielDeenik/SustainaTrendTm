<script lang="ts">
  import { fade } from 'svelte/transition';
  import { LineChart } from "@carbon/charts-svelte";
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Loading from '$lib/components/ui/Loading.svelte';
  import Alert from '$lib/components/ui/Alert.svelte';
  import { apiRequest } from '$lib/api/client';
  import type { APIError } from '$lib/api/client';
  import type { Metric } from '$lib/types/schema';
  import { onMount } from 'svelte';

  let metrics: Metric[] = [];
  let loading = true;
  let error: Error | APIError | null = null;

  // Group metrics by category for better visualization
  $: groupedMetrics = metrics.reduce((acc, metric) => {
    if (!acc[metric.category]) {
      acc[metric.category] = [];
    }
    acc[metric.category].push(metric);
    return acc;
  }, {} as Record<string, Metric[]>);

  // Prepare chart data
  $: chartData = metrics.map(m => ({
    group: m.category,
    date: new Date(m.timestamp),
    value: m.value
  }));

  $: chartOptions = {
    title: 'Sustainability Metrics Overview',
    axes: {
      bottom: {
        title: 'Time',
        mapsTo: 'date',
        scaleType: 'time'
      },
      left: {
        title: 'Value',
        mapsTo: 'value',
        scaleType: 'linear'
      }
    },
    height: '400px',
    theme: 'g90',
    legend: {
      alignment: 'center'
    },
    toolbar: {
      enabled: false
    }
  };

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

<div class="space-y-8" in:fade>
  <div class="flex justify-between items-center">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
      Sustainability Dashboard
    </h1>
    <button
      class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-opacity-90 transition-colors"
      on:click={fetchData}
      disabled={loading}
    >
      Refresh Data
    </button>
  </div>

  {#if loading}
    <div class="flex justify-center py-12">
      <Loading size="lg" />
    </div>
  {:else if error}
    <Alert variant="error">
      <div class="flex flex-col gap-2">
        <strong class="font-bold">Error!</strong>
        <p>{error.message}</p>
        <button
          class="mt-2 text-red-600 hover:text-red-700 underline"
          on:click={fetchData}
        >
          Try Again
        </button>
      </div>
    </Alert>
  {:else}
    <!-- Chart Section -->
    {#if metrics.length > 0}
      <Card>
        <div class="h-[400px]">
          <LineChart data={chartData} options={chartOptions} />
        </div>
      </Card>
    {/if}

    <!-- Metrics Grid -->
    {#each Object.entries(groupedMetrics) as [category, categoryMetrics]}
      <div class="mt-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white capitalize mb-4">
          {category} Metrics
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each categoryMetrics as metric (metric.id)}
            <Card>
              <div class="flex justify-between items-start">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {metric.name}
                </h3>
                <Badge variant={category === 'emissions' ? 'error' : 'default'}>
                  {category}
                </Badge>
              </div>
              <div class="mt-4">
                <p class="text-3xl font-bold text-primary">
                  {metric.value} {metric.unit}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
                  Last updated: {new Date(metric.timestamp).toLocaleString()}
                </p>
              </div>
            </Card>
          {/each}
        </div>
      </div>
    {/each}
  {/if}
</div>