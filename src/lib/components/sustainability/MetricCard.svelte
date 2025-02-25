<script lang="ts">
  import { fade } from 'svelte/transition';
  import { LineChart } from "@carbon/charts-svelte";
  import Card from '../ui/Card.svelte';
  import Alert from '../ui/Alert.svelte';
  import Badge from '../ui/Badge.svelte';
  import type { Metric } from '$lib/types/schema';
  import { analyzeMetric } from '$lib/services/ai';
  import { AnalyticsService } from '$lib/services/analytics';
  import type { AIAnalysis } from '$lib/services/ai';
  import type { AnalyticsResult } from '$lib/services/analytics';

  export let metric: Metric;
  export let historicalMetrics: Metric[] = [];
  export let aiEnabled = false;

  let aiAnalysis: AIAnalysis | null = null;
  let analytics: AnalyticsResult | null = null;
  let analyzing = false;
  let error: Error | null = null;

  // Calculate analytics whenever historical data changes
  $: if (historicalMetrics.length > 0) {
    analytics = AnalyticsService.calculateTrend([...historicalMetrics, metric]);
  }

  // Only fetch AI analysis when enabled and not already analyzing
  $: if (aiEnabled && !aiAnalysis && !analyzing && !error && analytics) {
    loadAnalysis();
  }

  async function loadAnalysis() {
    if (!aiEnabled) return;

    try {
      analyzing = true;
      error = null;
      aiAnalysis = await analyzeMetric(metric, historicalMetrics);
    } catch (err) {
      error = err instanceof Error ? err : new Error('Analysis failed');
      console.error('AI analysis failed:', error);
    } finally {
      analyzing = false;
    }
  }

  $: chartData = analytics?.timeSeriesData.map(point => ({
    group: metric.name,
    date: point.date,
    value: point.value
  })) ?? [];

  $: chartOptions = {
    title: 'Historical Trend',
    axes: {
      bottom: {
        title: 'Time',
        mapsTo: 'date',
        scaleType: 'time'
      },
      left: {
        title: metric.unit,
        mapsTo: 'value',
        scaleType: 'linear'
      }
    },
    height: '200px',
    theme: 'g90',
    toolbar: {
      enabled: false
    }
  };
</script>

<Card>
  <div class="flex flex-col" in:fade>
    <!-- Metric Header -->
    <div class="flex justify-between items-start">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        {metric.name}
      </h3>
      <Badge variant={metric.category === 'emissions' ? 'error' : 'default'}>
        {metric.category}
      </Badge>
    </div>

    <!-- Metric Value and Chart -->
    <div class="mt-4">
      <div class="flex justify-between items-baseline">
        <p class="text-3xl font-bold text-primary">
          {metric.value} {metric.unit}
        </p>
        {#if analytics}
          <div class="text-sm">
            <span class="font-medium">Avg:</span>
            <span class="text-gray-600 dark:text-gray-400">
              {analytics.historicalAverage.toFixed(1)} {metric.unit}
            </span>
          </div>
        {/if}
      </div>

      {#if analytics && chartData.length > 0}
        <div class="mt-4">
          <LineChart data={chartData} options={chartOptions} />
        </div>
      {/if}
    </div>

    <!-- Analytics Insights -->
    {#if analytics}
      <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
              Trend
            </h4>
            <span class="inline-block mt-1 px-2 py-1 text-xs font-medium rounded-full
              {analytics.trend === 'up' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100' :
               analytics.trend === 'down' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100' :
               'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100'}">
              {analytics.trend} ({analytics.percentageChange.toFixed(1)}%)
            </span>
          </div>

          <div>
            <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
              Statistics
            </h4>
            <div class="text-xs text-gray-600 dark:text-gray-400">
              <div>Min: {analytics.statistics.min.toFixed(1)}</div>
              <div>Max: {analytics.statistics.max.toFixed(1)}</div>
            </div>
          </div>
        </div>

        {#if analytics.insights.length > 0}
          <div class="mt-4">
            <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
              Key Insights
            </h4>
            <ul class="mt-1 space-y-2 text-sm text-gray-600 dark:text-gray-400">
              {#each analytics.insights as insight}
                <li class="flex items-start">
                  <span class="mr-2">•</span>
                  <span>{insight}</span>
                </li>
              {/each}
            </ul>
          </div>
        {/if}

        {#if analytics.anomalies}
          <Alert variant="warning" class="mt-4">
            <p class="text-sm">Anomaly detected: Current values show significant deviation from historical patterns.</p>
          </Alert>
        {/if}
      </div>
    {/if}

    <!-- AI Analysis Section -->
    {#if aiEnabled}
      <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        {#if analyzing}
          <div class="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <div class="animate-spin h-4 w-4 border-2 border-primary rounded-full border-t-transparent"></div>
            <span>Analyzing data...</span>
          </div>
        {:else if error}
          <Alert variant="error">
            <div class="flex flex-col gap-2">
              <p class="text-sm">{error.message}</p>
              <button
                class="text-sm underline hover:text-red-700 dark:hover:text-red-300"
                on:click={() => {
                  error = null;
                  loadAnalysis();
                }}
              >
                Try Again
              </button>
            </div>
          </Alert>
        {:else if aiAnalysis}
          <div class="space-y-4">
            <div>
              <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
                AI Analysis
              </h4>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {aiAnalysis.summary}
              </p>
            </div>

            <div>
              <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
                Recommendations
              </h4>
              <ul class="mt-1 space-y-2 text-sm text-gray-600 dark:text-gray-400">
                {#each aiAnalysis.recommendations as recommendation}
                  <li class="flex items-start">
                    <span class="mr-2">•</span>
                    <span>{recommendation}</span>
                  </li>
                {/each}
              </ul>
            </div>

            <div>
              <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
                Confidence
              </h4>
              <div class="mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-primary" 
                  style="width: {(aiAnalysis.confidence * 100)}%"
                />
              </div>
            </div>
          </div>
        {/if}
      </div>
    {/if}

    <!-- Metadata -->
    <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        Last updated: {new Date(metric.timestamp).toLocaleString()}
      </p>
    </div>
  </div>
</Card>