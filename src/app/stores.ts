import { readable } from 'svelte/store';

export const page = readable({
  url: {
    pathname: window.location.pathname,
    href: window.location.href,
    host: window.location.host,
    protocol: window.location.protocol,
  }
});
