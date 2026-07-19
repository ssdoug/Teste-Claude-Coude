// @ts-check
import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // TODO: substitua pelo domínio real antes do deploy (necessário para o sitemap)
  site: 'https://example.com',
  output: 'static',
  vite: {
    plugins: [tailwindcss()]
  },

  integrations: [mdx(), sitemap()]
});