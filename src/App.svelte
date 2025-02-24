<script lang="ts">
  import "./app.css";
  import { onMount } from 'svelte';
  import Card from './lib/components/ui/Card.svelte';
  import Badge from './lib/components/ui/Badge.svelte';
  import Loading from './lib/components/ui/Loading.svelte';
  import Navigation from './lib/components/Navigation.svelte';

  let metrics = [];
  let loading = true;
  let error = null;

  async function fetchLatestMetrics() {
    try {
      loading = true;
      error = null;
      const response = await fetch('/api/metrics');
      if (!response.ok) throw new Error('Failed to fetch metrics');
      metrics = await response.json();
    } catch (err) {
      error = err instanceof Error ? err : new Error('Failed to load metrics');
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
      <div class="card" style="background-color: #fee2e2; color: #991b1b;">
        <strong class="font-bold">Error!</strong>
        <p>{error.message}</p>
        <button 
          class="badge badge-error mt-4"
          on:click={fetchLatestMetrics}
        >
          Try Again
        </button>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
        <Card title="Environmental Impact">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span>Carbon Emissions</span>
              <Badge variant="error">Critical</Badge>
            </div>
            {#if metrics.find(m => m.category === 'emissions')}
              {@const emission = metrics.find(m => m.category === 'emissions')}
              <p class="text-2xl font-bold text-primary">{emission.value} {emission.unit}</p>
              <p class="card-subtitle">Latest measurement</p>
            {:else}
              <p class="text-2xl font-bold card-subtitle">No Data</p>
            {/if}
          </div>
        </Card>

        <Card title="Water Usage">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span>Consumption Rate</span>
              <Badge variant="warning">Moderate</Badge>
            </div>
            {#if metrics.find(m => m.category === 'water')}
              {@const water = metrics.find(m => m.category === 'water')}
              <p class="text-2xl font-bold text-primary">{water.value} {water.unit}</p>
              <p class="card-subtitle">Latest measurement</p>
            {:else}
              <p class="text-2xl font-bold card-subtitle">No Data</p>
            {/if}
          </div>
        </Card>

        <Card title="Energy Efficiency">
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span>Power Usage</span>
              <Badge variant="success">Optimal</Badge>
            </div>
            {#if metrics.find(m => m.category === 'energy')}
              {@const energy = metrics.find(m => m.category === 'energy')}
              <p class="text-2xl font-bold text-primary">{energy.value} {energy.unit}</p>
              <p class="card-subtitle">Latest measurement</p>
            {:else}
              <p class="text-2xl font-bold card-subtitle">No Data</p>
            {/if}
          </div>
        </Card>
      </div>
    {/if}
  </main>

  <footer class="nav mt-4">
    <div class="container text-center card-subtitle">
      © {new Date().getFullYear()} Sustainability Intelligence Platform
    </div>
  </footer>
</div>