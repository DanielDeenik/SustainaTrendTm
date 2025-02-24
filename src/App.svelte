<script lang="ts">
  import "./app.css";
  import { onMount } from 'svelte';
  import Card from './lib/components/ui/Card.svelte';
  import Badge from './lib/components/ui/Badge.svelte';
  import Loading from './lib/components/ui/Loading.svelte';
  import Navigation from './lib/components/Navigation.svelte';
  import { logger } from '$lib/services/logger';
  import { apiRequest } from '$lib/api/client';
  import type { Metric } from '$lib/types/schema';

  let metrics: Metric[] = [];
  let loading = true;
  let error: Error | null = null;

  async function fetchLatestMetrics() {
    try {
      loading = true;
      error = null;
      metrics = await apiRequest<Metric[]>('/api/metrics');
      logger.info('Dashboard metrics loaded', { count: metrics.length });
    } catch (err) {
      error = err instanceof Error ? err : new Error('Failed to load metrics');
      logger.error('Failed to load metrics', { error });
    } finally {
      loading = false;
    }
  }

  onMount(fetchLatestMetrics);
</script>

<div class="min-h-screen">
  <Navigation />

  <main class="container">
    <h1 class="text-2xl font-bold mb-4">
      Sustainability Intelligence Dashboard
    </h1>

    {#if loading}
      <div class="flex justify-center items-center" style="min-height: 200px;">
        <Loading size="lg" />
      </div>
    {:else if error}
      <div class="card" style="background-color: var(--error); color: white;">
        <strong class="font-bold">Error!</strong>
        <p>{error.message}</p>
        <button 
          class="badge badge-default mt-4"
          style="background: white; color: var(--error);"
          on:click={fetchLatestMetrics}
        >
          Try Again
        </button>
      </div>
    {:else}
      <div class="grid grid-cols-1">
        {#each ['emissions', 'water', 'energy'] as category}
          {#if metrics.find(m => m.category === category)}
            {@const metric = metrics.find(m => m.category === category)}
            <Card title={category === 'emissions' ? 'Environmental Impact' : 
                        category === 'water' ? 'Water Usage' : 'Energy Efficiency'}>
              <div class="space-y-4">
                <div class="flex justify-between items-center">
                  <span>{category === 'emissions' ? 'Carbon Emissions' :
                         category === 'water' ? 'Consumption Rate' : 'Power Usage'}</span>
                  <Badge variant={category === 'emissions' ? 'error' :
                                category === 'water' ? 'warning' : 'success'}>
                    {category === 'emissions' ? 'Critical' :
                     category === 'water' ? 'Moderate' : 'Optimal'}
                  </Badge>
                </div>
                <p class="text-2xl font-bold text-primary">{metric?.value} {metric?.unit}</p>
                <p class="card-subtitle">Latest measurement</p>
              </div>
            </Card>
          {/if}
        {/each}
      </div>
    {/if}
  </main>

  <footer class="nav mt-4">
    <div class="container text-center card-subtitle">
      © {new Date().getFullYear()} Sustainability Intelligence Platform
    </div>
  </footer>
</div>