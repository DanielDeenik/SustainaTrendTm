<script lang="ts">
  export let variant: 'default' | 'error' | 'success' | 'warning' = 'default';

  const variantClasses = {
    default: 'bg-blue-50 text-blue-800 dark:bg-blue-900 dark:text-blue-100',
    error: 'bg-red-50 text-red-800 dark:bg-red-900 dark:text-red-100',
    success: 'bg-green-50 text-green-800 dark:bg-green-900 dark:text-green-100',
    warning: 'bg-yellow-50 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
  };

  const iconClasses = {
    default: 'text-blue-400 dark:text-blue-300',
    error: 'text-red-400 dark:text-red-300',
    success: 'text-green-400 dark:text-green-300',
    warning: 'text-yellow-400 dark:text-yellow-300'
  };
</script>

<div class="rounded-lg p-4 {variantClasses[variant]} flex items-start space-x-3" role="alert">
  <div class="flex-1">
    <slot />
  </div>
</div>