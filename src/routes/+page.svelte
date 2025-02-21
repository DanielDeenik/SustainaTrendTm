<script lang="ts">
  import { onMount } from 'svelte';
  import { Search } from 'lucide-svelte';
  import { sustainabilityMetrics, isLoading, error, fetchSustainabilityMetrics } from '$lib/stores/sustainability';
  import MetricCard from '$lib/components/sustainability/metric-card.svelte';

  let searchQuery = "";
  let demoCompanyId = "demo-company-1"; // For demonstration

  onMount(() => {
    fetchSustainabilityMetrics(demoCompanyId);
  });

  $: filteredMetrics = $sustainabilityMetrics.filter(metric => 
    JSON.stringify(metric).toLowerCase().includes(searchQuery.toLowerCase())
  );
</script>

<div class="flex flex-col items-center justify-center space-y-8">
  <h1 class="text-4xl font-bold text-primary">Welcome to Sustainability Intelligence</h1>

  <div class="w-full max-w-2xl">
    <div class="relative">
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search sustainability metrics..."
        class="w-full px-4 py-2 pl-10 border rounded-lg"
      />
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
    </div>
  </div>

  {#if $isLoading}
    <div class="text-center">Loading sustainability metrics...</div>
  {:else if $error}
    <div class="text-red-500">{$error}</div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-6xl">
      {#each filteredMetrics as metrics}
        <MetricCard
          title="Environmental Metrics"
          metrics={metrics.environmental}
          type="environmental"
        />
        <MetricCard
          title="Social Metrics"
          metrics={metrics.social}
          type="social"
        />
        <MetricCard
          title="Governance Metrics"
          metrics={metrics.governance}
          type="governance"
        />
      {/each}
    </div>
  {/if}
</div>