// frontend/vite.config.js

import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [
		// L'ordre est parfois important. tailwindcss() peut être placé ici.
		tailwindcss(), 
		sveltekit()
	],
	test: {
		// Configuration Vitest simplifiée et fonctionnelle
		include: ['src/**/*.{test,spec}.{js,ts}'],
		environment: 'jsdom',
		setupFiles: ['./vitest-setup-client.js'],
	}
});