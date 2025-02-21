<script lang="ts">
  import { Search } from 'lucide-svelte';
</script>

<div class="container mx-auto px-4 py-8">
  <h1 class="text-4xl font-bold mb-8">Sustainability Intelligence Platform</h1>
  
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex gap-4 mb-6">
      <div class="flex-1 relative">
        <input 
          type="text"
          placeholder="Search sustainability insights..."
          class="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <Search class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
      </div>
      <button class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
        Search
      </button>
    </div>
    
    <div class="space-y-4">
      <div class="p-4 border rounded-lg">
        <h2 class="text-xl font-semibold mb-2">Recent Trends</h2>
        <p class="text-gray-600">No trends available yet. Start by searching for sustainability metrics.</p>
      </div>
      
      <div class="p-4 border rounded-lg">
        <h2 class="text-xl font-semibold mb-2">AI Insights</h2>
        <p class="text-gray-600">AI-powered insights will appear here after analysis.</p>
      </div>
    </div>
  </div>
</div>
