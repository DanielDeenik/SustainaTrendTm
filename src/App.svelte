<script lang="ts">
  import "./app.css";
  import { onMount } from 'svelte';
  import { logger } from '$lib/services/logger';

  let route = window.location.pathname;
  let metrics = [];
  let loading = true;
  let error = null;

  async function fetchMetrics() {
    try {
      loading = true;
      error = null;
      const response = await fetch('http://0.0.0.0:8000/api/metrics');
      if (!response.ok) throw new Error('Failed to fetch metrics');
      metrics = await response.json();
      logger.info('Dashboard metrics loaded', { count: metrics.length });
    } catch (err) {
      error = err instanceof Error ? err : new Error('Failed to load metrics');
      logger.error('Failed to load metrics', { error });
    } finally {
      loading = false;
    }
  }

  onMount(fetchMetrics);

  function navigate(path) {
    route = path;
    window.history.pushState(null, '', path);
  }

  window.addEventListener('popstate', () => {
    route = window.location.pathname;
  });
</script>

<div class="min-h-screen">
  <nav class="nav">
    <div class="container">
      <div class="nav-content">
        <div class="nav-brand">Sustainability Intelligence</div>
        <div class="nav-links">
          <button 
            class="nav-link {route === '/' ? 'active' : ''}"
            on:click={() => navigate('/')}
          >
            Dashboard
          </button>
          <button 
            class="nav-link {route === '/metrics' ? 'active' : ''}"
            on:click={() => navigate('/metrics')}
          >
            Metrics
          </button>
          <button 
            class="nav-link {route === '/reports' ? 'active' : ''}"
            on:click={() => navigate('/reports')}
          >
            Reports
          </button>
        </div>
      </div>
    </div>
  </nav>

  <main class="container">
    {#if loading}
      <div class="loading">
        <div class="spinner"></div>
      </div>
    {:else if error}
      <div class="error">
        <strong>Error!</strong>
        <p>{error.message}</p>
        <button class="retry-button" on:click={fetchMetrics}>
          Try Again
        </button>
      </div>
    {:else}
      <div class="grid">
        {#each metrics as metric}
          <div class="card">
            <h3 class="card-title">{metric.name}</h3>
            <div class="metric-content">
              <div class="metric-header">
                <span>{metric.category}</span>
                <span class="badge {metric.category}">{metric.category}</span>
              </div>
              <p class="metric-value">{metric.value} {metric.unit}</p>
              <p class="metric-timestamp">Latest measurement</p>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </main>

  <footer class="footer">
    <div class="container">
      © {new Date().getFullYear()} Sustainability Intelligence Platform
    </div>
  </footer>
</div>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .nav {
    background: white;
    border-bottom: 1px solid #e5e7eb;
    padding: 1rem 0;
  }

  .nav-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .nav-brand {
    font-size: 1.25rem;
    font-weight: bold;
    color: var(--primary);
  }

  .nav-links {
    display: flex;
    gap: 2rem;
  }

  .nav-link {
    color: #4b5563;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border: none;
    background: none;
    cursor: pointer;
    border-radius: 0.375rem;
  }

  .nav-link:hover {
    background: #f3f4f6;
  }

  .nav-link.active {
    color: var(--primary);
    background: #f3f4f6;
  }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
  }

  .spinner {
    border: 3px solid #f3f3f3;
    border-top: 3px solid var(--primary);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .error {
    background: #fee2e2;
    border: 1px solid #ef4444;
    color: #991b1b;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
  }

  .retry-button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 0.375rem;
    cursor: pointer;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
  }

  .card {
    background: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .card-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }

  .metric-content {
    padding: 1rem 0;
  }

  .metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
  }

  .badge.emissions {
    background: #fee2e2;
    color: #991b1b;
  }

  .badge.water {
    background: #e0f2fe;
    color: #075985;
  }

  .badge.energy {
    background: #d1fae5;
    color: #065f46;
  }

  .metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary);
  }

  .metric-timestamp {
    font-size: 0.875rem;
    color: #6b7280;
    margin-top: 0.5rem;
  }

  .footer {
    margin-top: 2rem;
    padding: 1.5rem 0;
    border-top: 1px solid #e5e7eb;
    text-align: center;
    color: #6b7280;
  }
</style>