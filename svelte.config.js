import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter(),
		csrf: {
			checkOrigin: false,
		},
    server: {
      host: '0.0.0.0',
      port: 3001,
      strictPort: true,
    }
	},
	preprocess: vitePreprocess()
};

export default config;