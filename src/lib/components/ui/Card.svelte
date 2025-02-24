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
    <div class="mt-4">
      <slot />
    </div>
  </div>
</div>

<style>
.card {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.card-subtitle {
  color: #6B7280;
  font-size: 0.875rem;
}
</style>