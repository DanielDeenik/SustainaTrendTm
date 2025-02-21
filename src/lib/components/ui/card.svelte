<script lang="ts">
  import { cn } from "$lib/utils";
  import type { HTMLAttributes } from "svelte/elements";

  interface $$Props extends HTMLAttributes<HTMLDivElement> {
    class?: string;
  }

  let { class: className = "", ...props } = $props();
</script>

<div
  class={cn(
    "rounded-lg border bg-card text-card-foreground shadow-sm",
    className
  )}
  {...props}
>
  <slot />
</div>
