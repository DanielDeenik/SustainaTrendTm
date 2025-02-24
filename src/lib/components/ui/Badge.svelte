<script lang="ts">
  export let variant: 'default' | 'success' | 'warning' | 'error' = 'default';
</script>

<span class="badge badge-{variant}">
  <slot />
</span>

<style>
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: capitalize;
}

.badge-default {
  background-color: #F3F4F6;
  color: #1F2937;
}

.badge-success {
  background-color: #D1FAE5;
  color: #065F46;
}

.badge-warning {
  background-color: #FEF3C7;
  color: #92400E;
}

.badge-error {
  background-color: #FEE2E2;
  color: #991B1B;
}
</style>