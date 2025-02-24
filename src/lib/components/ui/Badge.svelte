<script lang="ts">
  export let variant: 'default' | 'success' | 'warning' | 'error' = 'default';
</script>

<span class="badge badge-{variant}">
  <slot />
</span>