import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter(),
		csrf: {
			checkOrigin: false,
		},
    // Add Vite configuration
    vite: {
      server: {
        host: '0.0.0.0',
        port: 3000,
        strictPort: true,
        // Allow Replit domain
        hmr: {
          clientPort: 443
        }
      }
    }
	},
	preprocess: vitePreprocess()
};

export default config;