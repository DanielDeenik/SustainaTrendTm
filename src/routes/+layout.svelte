<script lang="ts">
  import "../app.css";
</script>

<div class="min-h-screen">
  <header class="border-b">
    <nav class="container mx-auto px-4 py-4">
      <h1 class="text-2xl font-bold text-primary">Sustainability Intelligence</h1>
    </nav>
  </header>

  <main class="container mx-auto px-4 py-8">
    <slot />
  </main>

  <footer class="border-t mt-auto">
    <div class="container mx-auto px-4 py-4 text-center text-gray-600">
      © {new Date().getFullYear()} Sustainability Intelligence Platform
    </div>
  </footer>
</div>
