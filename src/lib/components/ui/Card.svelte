<script lang="ts">
  export let title: string;
  export let subtitle: string | undefined = undefined;
</script>

<div class="card">
  <div class="space-y-4">
    <h3 class="card-title">
      {title}
    </h3>
    {#if subtitle}
      <p class="card-subtitle">
        {subtitle}
      </p>
    {/if}
  </div>
  <div class="mt-4">
    <slot />
  </div>
</div>