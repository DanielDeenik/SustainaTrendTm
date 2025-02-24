<script lang="ts">
  import { fade } from 'svelte/transition';
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';
  import Loading from '$lib/components/ui/Loading.svelte';
  import { onMount } from 'svelte';
  import { logger } from '$lib/services/logger';

  let metrics = [];
  let loading = true;
  let error = null;

  async function fetchMetrics() {
    try {
      loading = true;
      error = null;
      const response = await fetch('http://0.0.0.0:8000/api/metrics');
      if (!response.ok) throw new Error('Failed to fetch metrics');
      metrics = await response.json();
      logger.info('Dashboard metrics loaded', { count: metrics.length });
    } catch (err) {
      error = err instanceof Error ? err : new Error('Failed to load metrics');
      logger.error('Failed to load metrics', { error });
    } finally {
      loading = false;
    }
  }

  onMount(fetchMetrics);
</script>

<div class="space-y-6" in:fade>
  <h1 class="text-3xl font-bold mb-8">
    Sustainability Intelligence Dashboard
  </h1>

  {#if loading}
    <div class="loading">
      <Loading size="lg" />
    </div>
  {:else if error}
    <div class="error">
      <strong>Error!</strong>
      <p>{error.message}</p>
      <button class="retry-button" on:click={fetchMetrics}>
        Try Again
      </button>
    </div>
  {:else}
    <div class="grid">
      {#each metrics as metric}
        <Card title={metric.name}>
          <div class="metric-content">
            <div class="metric-header">
              <span>{metric.category}</span>
              <Badge variant={metric.category === 'emissions' ? 'error' : 'default'}>
                {metric.category}
              </Badge>
            </div>
            <p class="metric-value">{metric.value} {metric.unit}</p>
            <p class="metric-timestamp">Latest measurement</p>
          </div>
        </Card>
      {/each}
    </div>
  {/if}
</div>

<style>
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
}

.error {
  background: #fee2e2;
  border: 1px solid #ef4444;
  color: #991b1b;
  padding: 1rem;
  border-radius: 0.5rem;
  margin: 1rem 0;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin: 1.5rem 0;
}

.metric-content {
  padding: 1rem 0;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary);
}

.metric-timestamp {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}
</style>