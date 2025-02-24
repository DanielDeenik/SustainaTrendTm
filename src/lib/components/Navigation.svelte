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

<nav class="nav" transition:fade>
  <div class="container">
    <div class="nav-content">
      <div class="flex">
        <div class="nav-brand">
          <span>Sustainability Intelligence</span>
        </div>
        <div class="nav-links">
          {#each routes as route}
            <a
              href={route.href}
              class="nav-link {$page.url.pathname === route.href ? 'active' : ''}"
            >
              <svelte:component this={route.icon} class="w-4 h-4" />
              {route.label}
            </a>
          {/each}
        </div>
      </div>
    </div>
  </div>

  <!-- Mobile menu -->
  <div class="nav-mobile">
    <div class="nav-mobile-content">
      {#each routes as route}
        <a
          href={route.href}
          class="nav-link {$page.url.pathname === route.href ? 'active' : ''}"
        >
          <svelte:component this={route.icon} class="w-5 h-5" />
          {route.label}
        </a>
      {/each}
    </div>
  </div>
</nav>

<style>
.nav-mobile {
  display: none;
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .nav-mobile {
    display: block;
    padding: 1rem;
  }

  .nav-mobile-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>