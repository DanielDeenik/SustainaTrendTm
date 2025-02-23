<script lang="ts">
  import "../app.css";
  import { fade } from 'svelte/transition';
  import Navigation from '$lib/components/Navigation.svelte';
  import ErrorBoundary from '$lib/components/ErrorBoundary.svelte';
  import { dev } from '$app/environment';
  import { logger } from '$lib/services/logger';

  // Log application startup
  logger.info('Application initialized', { dev });
</script>

<ErrorBoundary>
  <div class="min-h-screen bg-white dark:bg-gray-900" in:fade>
    <Navigation />

    <main class="max-w-7xl mx-auto px-4 py-8">
      <slot />
    </main>

    <footer class="border-t border-gray-200 dark:border-gray-800 mt-auto">
      <div class="max-w-7xl mx-auto px-4 py-4 text-center text-gray-600 dark:text-gray-400">
        © {new Date().getFullYear()} Sustainability Intelligence Platform
      </div>
    </footer>
  </div>
</ErrorBoundary>