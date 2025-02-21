<script lang="ts">
  import { Search } from 'lucide-svelte';
</script>

<div class="flex flex-col items-center justify-center space-y-8">
  <h1 class="text-4xl font-bold text-primary">Welcome to Sustainability Intelligence</h1>
  
  <div class="w-full max-w-2xl">
    <div class="relative">
      <input
        type="text"
        placeholder="Search sustainability metrics..."
        class="w-full px-4 py-2 pl-10 border rounded-lg"
      />
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-6xl">
    <div class="p-6 rounded-lg border hover:shadow-lg transition-shadow">
      <h3 class="text-xl font-semibold mb-2">Carbon Metrics</h3>
      <p class="text-gray-600">Track and analyze carbon emissions data.</p>
    </div>
    <div class="p-6 rounded-lg border hover:shadow-lg transition-shadow">
      <h3 class="text-xl font-semibold mb-2">Energy Usage</h3>
      <p class="text-gray-600">Monitor energy consumption patterns.</p>
    </div>
    <div class="p-6 rounded-lg border hover:shadow-lg transition-shadow">
      <h3 class="text-xl font-semibold mb-2">Waste Management</h3>
      <p class="text-gray-600">Optimize waste reduction strategies.</p>
    </div>
  </div>
</div>
