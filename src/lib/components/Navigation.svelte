<script lang="ts">
  import { page } from '$app/stores';
  import { fade } from 'svelte/transition';
  import { BarChart3, FileText, Activity } from 'lucide-svelte';

  const routes = [
    { href: '/', label: 'Dashboard', icon: Activity },
    { href: '/metrics', label: 'Metrics', icon: BarChart3 },
    { href: '/reports', label: 'Reports', icon: FileText }
  ];
</script>

<nav class="bg-white dark:bg-gray-800 shadow-sm" transition:fade>
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex justify-between h-16">
      <div class="flex">
        <div class="flex-shrink-0 flex items-center">
          <span class="text-2xl font-bold text-primary">Sustainability Intelligence</span>
        </div>
        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
          {#each routes as route}
            <a
              href={route.href}
              class="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium
              {$page.url.pathname === route.href
                ? 'border-primary text-gray-900 dark:text-white'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'}"
            >
              <svelte:component this={route.icon} class="w-4 h-4 mr-2" />
              {route.label}
            </a>
          {/each}
        </div>
      </div>
    </div>
  </div>

  <!-- Mobile menu -->
  <div class="sm:hidden">
    <div class="pt-2 pb-3 space-y-1">
      {#each routes as route}
        <a
          href={route.href}
          class="flex items-center px-3 py-2 text-base font-medium
          {$page.url.pathname === route.href
            ? 'bg-primary bg-opacity-10 text-primary'
            : 'text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'}"
        >
          <svelte:component this={route.icon} class="w-5 h-5 mr-3" />
          {route.label}
        </a>
      {/each}
    </div>
  </div>
</nav>
