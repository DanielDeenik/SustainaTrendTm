<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import type { Report } from '$lib/types/schema';
  import { apiRequest } from '$lib/api/client';
  import Alert from '$lib/components/ui/Alert.svelte';
  import Loading from '$lib/components/ui/Loading.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Badge from '$lib/components/ui/Badge.svelte';

  let reports: Report[] = [];
  let loading = true;
  let error: Error | null = null;

  async function fetchReports() {
    try {
      loading = true;
      reports = await apiRequest<Report[]>('/api/reports');
      error = null;
    } catch (err) {
      console.error('Error fetching reports:', err);
      error = err instanceof Error ? err : new Error('Failed to load reports');
    } finally {
      loading = false;
    }
  }

  onMount(fetchReports);

  function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  function getStatusVariant(status: string): 'success' | 'warning' | 'default' {
    switch (status) {
      case 'published': return 'success';
      case 'draft': return 'warning';
      default: return 'default';
    }
  }
</script>

<div class="space-y-6" in:fade>
  <div class="flex justify-between items-center">
    <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
      Sustainability Reports
    </h2>
  </div>

  {#if loading}
    <Loading size="lg" />
  {:else if error}
    <Alert variant="error">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline ml-2">{error.message}</span>
      <button
        class="mt-4 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        on:click={fetchReports}
      >
        Retry
      </button>
    </Alert>
  {:else if reports.length === 0}
    <Alert variant="default">
      <p>No reports available.</p>
    </Alert>
  {:else}
    <div class="grid grid-cols-1 gap-6">
      {#each reports as report}
        <Card 
          title={report.title}
          subtitle={report.description}
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="grid grid-cols-2 gap-4 text-sm text-gray-500 dark:text-gray-400">
                <div>
                  <span class="font-medium">Period Start:</span>
                  <p>{formatDate(report.period_start)}</p>
                </div>
                <div>
                  <span class="font-medium">Period End:</span>
                  <p>{formatDate(report.period_end)}</p>
                </div>
              </div>
            </div>
            <Badge variant={getStatusVariant(report.status)}>
              {report.status}
            </Badge>
          </div>
          {#if report.data && Object.keys(report.data).length > 0}
            <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Report Data
              </h4>
              <div class="space-y-1 text-sm text-gray-500 dark:text-gray-400">
                {#each Object.entries(report.data) as [key, value]}
                  <p class="capitalize">{key}: {value}</p>
                {/each}
              </div>
            </div>
          {/if}
        </Card>
      {/each}
    </div>
  {/if}
</div>