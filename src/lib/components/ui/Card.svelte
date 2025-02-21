<script lang="ts">
  export let title: string;
  export let subtitle: string | undefined = undefined;
</script>

<div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
  <div class="space-y-1">
    <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
      {title}
    </h3>
    {#if subtitle}
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {subtitle}
      </p>
    {/if}
  </div>
  <div class="mt-4">
    <slot />
  </div>
</div>
