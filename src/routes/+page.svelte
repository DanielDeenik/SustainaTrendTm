<script lang="ts">
  import { fade } from 'svelte/transition';
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';

  let pageTitle = "Sustainability Intelligence Dashboard";
</script>

<div class="space-y-6" in:fade>
  <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-8">
    {pageTitle}
  </h1>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <Card title="Environmental Impact">
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <span class="text-gray-600 dark:text-gray-400">Carbon Emissions</span>
          <Badge variant="error">Critical</Badge>
        </div>
        <p class="text-2xl font-bold text-primary">-15%</p>
        <p class="text-sm text-gray-500">Reduction from last quarter</p>
      </div>
    </Card>

    <Card title="Water Usage">
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <span class="text-gray-600 dark:text-gray-400">Consumption Rate</span>
          <Badge variant="warning">Moderate</Badge>
        </div>
        <p class="text-2xl font-bold text-primary">245K</p>
        <p class="text-sm text-gray-500">Gallons per month</p>
      </div>
    </Card>

    <Card title="Energy Efficiency">
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <span class="text-gray-600 dark:text-gray-400">Power Usage</span>
          <Badge variant="success">Optimal</Badge>
        </div>
        <p class="text-2xl font-bold text-primary">92%</p>
        <p class="text-sm text-gray-500">Renewable sources</p>
      </div>
    </Card>
  </div>
</div>