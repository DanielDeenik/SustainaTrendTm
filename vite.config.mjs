import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    target: 'esnext',
    modulePreload: {
      polyfill: true
    }
  }
});