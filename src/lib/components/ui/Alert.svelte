<script lang="ts">
  export let variant: 'default' | 'error' | 'success' | 'warning' = 'default';
  
  const variantClasses = {
    default: 'bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-100',
    error: 'bg-red-100 text-red-700 dark:bg-red-800 dark:text-red-100',
    success: 'bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-100',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-800 dark:text-yellow-100'
  };
</script>

<div class="rounded-lg p-4 {variantClasses[variant]}" role="alert">
  <slot />
</div>
