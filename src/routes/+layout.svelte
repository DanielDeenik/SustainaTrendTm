<script lang="ts">
  import "../app.css";
</script>

<div class="min-h-screen bg-white dark:bg-gray-900">
  <header class="border-b border-gray-200 dark:border-gray-800">
    <nav class="container mx-auto px-4 py-4">
      <h1 class="text-2xl font-bold text-primary">Sustainability Intelligence</h1>
    </nav>
  </header>

  <main class="container mx-auto px-4 py-8">
    <slot />
  </main>

  <footer class="border-t border-gray-200 dark:border-gray-800 mt-auto">
    <div class="container mx-auto px-4 py-4 text-center text-gray-600 dark:text-gray-400">
      © {new Date().getFullYear()} Sustainability Intelligence Platform
    </div>
  </footer>
</div>