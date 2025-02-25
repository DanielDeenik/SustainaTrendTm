<script lang="ts">
  import { browser } from '$app/environment';
  import { logger } from '$lib/services/logger';
  import Alert from './ui/Alert.svelte';
  import type { APIError } from '$lib/api/client';

  let error: Error | null = null;

  if (browser) {
    window.addEventListener('error', (event) => {
      error = event.error;
      logger.error('Error caught by boundary:', error);
    });
  }
</script>

{#if error}
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-lg w-full">
      <Alert variant="error">
        <h2 class="text-2xl font-bold mb-4">
          Something went wrong
        </h2>
        <p class="mb-4">
          {error.message}
        </p>
        <div class="flex justify-between items-center">
          <button
            class="bg-primary text-white px-4 py-2 rounded hover:bg-opacity-90 transition-colors"
            on:click={() => window.location.reload()}
          >
            Reload Page
          </button>
          <a
            href="/"
            class="text-primary hover:underline"
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