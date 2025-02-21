<script lang="ts">
  import { onMount } from 'svelte';
  import { Search } from 'lucide-svelte';
  import { sustainabilityMetrics, isLoading, error, fetchSustainabilityMetrics } from '$lib/stores/sustainability';

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
        <div class="p-6 rounded-lg border hover:shadow-lg transition-shadow">
          <h3 class="text-xl font-semibold mb-4">ESG Metrics Overview</h3>

          <div class="space-y-4">
            <div>
              <h4 class="font-medium text-primary">Environmental</h4>
              <p>Carbon Emissions: {metrics.environmental.carbonEmissions}</p>
              <p>Energy Usage: {metrics.environmental.energyUsage}</p>
            </div>

            <div>
              <h4 class="font-medium text-secondary">Social</h4>
              <p>Employee Satisfaction: {metrics.social.employeeSatisfaction}%</p>
              <p>Diversity Score: {metrics.social.diversityScore}%</p>
            </div>

            <div>
              <h4 class="font-medium text-accent">Governance</h4>
              <p>Policy Compliance: {metrics.governance.policyCompliance}%</p>
              <p>Risk Management: {metrics.governance.riskManagementScore}%</p>
            </div>

            <div class="mt-4 pt-4 border-t">
              <p class="font-bold">Overall Score: {metrics.overallScore}%</p>
              <p class="text-sm text-gray-500">Last Updated: {new Date(metrics.lastUpdated).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>