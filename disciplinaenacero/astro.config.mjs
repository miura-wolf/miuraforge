// astro.config.mjs — disciplinaenacero.com
// Configuración optimizada para Netlify Image CDN + SEO máximo
import { defineConfig } from 'astro/config';
import netlify from '@astrojs/netlify';

export default defineConfig({
  site: 'https://disciplinaenacero.com',
  output: 'static',
  adapter: netlify(),
  image: {
    domains: [
      'images.unsplash.com',
      'picsum.photos',
      'amzn.to',
      'm.media-amazon.com',   // imágenes de portadas Amazon
    ],
  },
  vite: {
    build: {
      rollupOptions: {
        output: { manualChunks: undefined },
      },
    },
  },
});
