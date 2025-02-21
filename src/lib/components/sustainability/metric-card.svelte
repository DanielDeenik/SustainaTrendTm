<script lang="ts">
  import type { EnvironmentalMetrics, SocialMetrics, GovernanceMetrics } from '$lib/types/sustainability';
  import { Card } from '$lib/components/ui/card';

  export let title: string;
  export let metrics: EnvironmentalMetrics | SocialMetrics | GovernanceMetrics;
  export let type: 'environmental' | 'social' | 'governance';

  // Define color classes based on metric type
  const colorClasses = {
    environmental: 'text-primary',
    social: 'text-secondary',
    governance: 'text-accent'
  };

  // Format number with 2 decimal places
  const formatNumber = (num: number) => num.toFixed(2);
</script>

<Card class="p-4 hover:shadow-lg transition-shadow">
  <h3 class="text-xl font-semibold mb-4 {colorClasses[type]}">{title}</h3>
  <div class="space-y-2">
    {#if type === 'environmental'}
      {@const env = metrics as EnvironmentalMetrics}
      <p>Carbon Emissions: {formatNumber(env.carbonEmissions)}</p>
      <p>Energy Usage: {formatNumber(env.energyUsage)} kWh</p>
      <p>Renewable Energy: {formatNumber(env.renewableEnergyPercentage)}%</p>
    {:else if type === 'social'}
      {@const soc = metrics as SocialMetrics}
      <p>Employee Satisfaction: {formatNumber(soc.employeeSatisfaction)}%</p>
      <p>Diversity Score: {formatNumber(soc.diversityScore)}%</p>
      <p>Health & Safety Incidents: {soc.healthAndSafetyIncidents}</p>
    {:else}
      {@const gov = metrics as GovernanceMetrics}
      <p>Policy Compliance: {formatNumber(gov.policyCompliance)}%</p>
      <p>Risk Management: {formatNumber(gov.riskManagementScore)}%</p>
      <p>Board Diversity: {formatNumber(gov.boardDiversity)}%</p>
    {/if}
  </div>
</Card>
