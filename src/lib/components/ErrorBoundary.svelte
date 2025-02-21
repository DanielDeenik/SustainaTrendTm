<script lang="ts">
  import { onError } from 'svelte';
  import { page } from '$app/stores';
  import { logger } from '$lib/services/logger';
  import Alert from './ui/Alert.svelte';
  import type { APIError } from '$lib/api/client';

  let error: Error | null = null;
  let isAPIError = false;

  onError(({ error: e }) => {
    error = e;
    isAPIError = e instanceof Error && 'requestId' in e;
    logger.error('Error caught by boundary:', e);
  });
</script>

{#if error}
  <div class="min-h-screen bg-red-50 dark:bg-red-900 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-lg w-full">
      <Alert variant="error">
        <h2 class="text-2xl font-bold mb-4">
          Something went wrong
        </h2>
        <p class="mb-4">
          {error.message}
        </p>
        {#if isAPIError}
          <p class="text-sm mb-4">
            Request ID: {(error as APIError).requestId || 'N/A'}
          </p>
        {/if}
        <div class="flex justify-between items-center">
          <button
            class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
            on:click={() => window.location.reload()}
          >
            Reload Page
          </button>
          <a
            href="/"
            class="text-red-600 dark:text-red-400 hover:underline"
          >
            Go to Home
          </a>
        </div>
      </Alert>
    </div>
  </div>
{:else}
  <slot />
{/if}