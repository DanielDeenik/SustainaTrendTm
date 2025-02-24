<script lang="ts">
  import { fade } from 'svelte/transition';
  import { Activity, BarChart3, FileText } from 'lucide-svelte';

  const routes = [
    { href: '/', label: 'Dashboard', icon: Activity },
    { href: '/metrics', label: 'Metrics', icon: BarChart3 },
    { href: '/reports', label: 'Reports', icon: FileText }
  ];

  let currentPath = window.location.pathname;

  window.addEventListener('popstate', () => {
    currentPath = window.location.pathname;
  });
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
              class="nav-link {currentPath === route.href ? 'active' : ''}"
            >
              <svelte:component this={route.icon} class="w-4 h-4" />
              {route.label}
            </a>
          {/each}
        </div>
      </div>
    </div>
  </div>
</nav>

<style>
.nav {
  background-color: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 0;
}

.container {
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 1rem;
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: #22c55e;
}

.nav-links {
  display: flex;
  gap: 2rem;
  margin-left: 2rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4b5563;
  text-decoration: none;
  padding: 0.5rem 0;
}

.nav-link:hover {
  color: #111827;
}

.nav-link.active {
  color: #22c55e;
  border-bottom: 2px solid #22c55e;
}
</style>