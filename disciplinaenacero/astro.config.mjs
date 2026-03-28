// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';

import netlify from '@astrojs/netlify';

import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
	site: 'https://disciplinaenacero.com',
	integrations: [mdx(), sitemap()],
	adapter: netlify(),
	image: {
		domains: ['images.unsplash.com', 'picsum.photos', 'm.media-amazon.com'],
	},

	vite: {
		plugins: [tailwindcss()],
	},
});