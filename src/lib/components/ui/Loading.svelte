<script lang="ts">
  export let size: 'sm' | 'md' | 'lg' = 'md';
  
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };
</script>

<div class="flex justify-center items-center">
  <div class="animate-spin rounded-full border-b-2 border-primary {sizeClasses[size]}" />
</div>
