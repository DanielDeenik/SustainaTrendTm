<script lang="ts">
  import { fade } from 'svelte/transition';
  import Card from '../ui/Card.svelte';
  import Alert from '../ui/Alert.svelte';
  import type { Metric } from '$lib/types/schema';
  import { analyzeMetric } from '$lib/services/ai';
  import type { AIAnalysis } from '$lib/services/ai';

  export let metric: Metric;
  export let aiEnabled = false;

  let aiAnalysis: AIAnalysis | null = null;
  let analyzing = false;
  let error: Error | null = null;

  // Only fetch AI analysis when enabled and not already analyzing
  $: if (aiEnabled && !aiAnalysis && !analyzing && !error) {
    loadAnalysis();
  }

  async function loadAnalysis() {
    if (!aiEnabled) return;

    try {
      analyzing = true;
      error = null;
      aiAnalysis = await analyzeMetric(metric);
    } catch (err) {
      error = err instanceof Error ? err : new Error('Analysis failed');
      console.error('AI analysis failed:', error);
    } finally {
      analyzing = false;
    }
  }

  function getCategoryStyle(category: string) {
    const styles = {
      emissions: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
      water: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100',
      energy: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
      default: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100'
    };
    return styles[category] || styles.default;
  }
</script>

<Card>
  <div class="flex flex-col" in:fade>
    <!-- Metric Header -->
    <div class="flex justify-between items-start mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        {metric.name}
      </h3>
      <span class="px-2 py-1 rounded-full text-sm font-medium {getCategoryStyle(metric.category)}">
        {metric.category}
      </span>
    </div>

    <!-- Metric Value -->
    <p class="text-3xl font-bold text-green-600 dark:text-green-400">
      {metric.value} {metric.unit}
    </p>

    <!-- AI Analysis Section -->
    {#if aiEnabled}
      <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        {#if analyzing}
          <div class="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <div class="animate-spin h-4 w-4 border-2 border-green-500 rounded-full border-t-transparent"></div>
            <span>Analyzing data...</span>
          </div>
        {:else if error}
          <Alert variant="error">
            <p class="text-sm">{error.message}</p>
            <button
              class="mt-2 text-sm underline"
              on:click={() => {
                error = null;
                loadAnalysis();
              }}
            >
              Try Again
            </button>
          </Alert>
        {:else if aiAnalysis}
          <div class="space-y-2">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {aiAnalysis.summary}
            </p>
            <div class="flex items-center space-x-2">
              <span class="text-xs font-medium uppercase {
                aiAnalysis.trend === 'increasing' ? 'text-green-600 dark:text-green-400' :
                aiAnalysis.trend === 'decreasing' ? 'text-red-600 dark:text-red-400' :
                'text-gray-600 dark:text-gray-400'
              }">
                {aiAnalysis.trend}
              </span>
            </div>
            {#if aiAnalysis.recommendations.length > 0}
              <ul class="text-sm text-gray-600 dark:text-gray-400 list-disc list-inside">
                {#each aiAnalysis.recommendations as recommendation}
                  <li>{recommendation}</li>
                {/each}
              </ul>
            {/if}
          </div>
        {/if}
      </div>
    {/if}

    <!-- Timestamp -->
    <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
      Last updated: {new Date(metric.timestamp).toLocaleString()}
    </p>
  </div>
</Card>