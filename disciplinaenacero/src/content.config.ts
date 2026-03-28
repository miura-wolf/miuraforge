// src/content.config.ts — disciplinaenacero.com
// Schema Zod que valida el frontmatter generado por forge_blog.py
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title:       z.string(),
    slug:        z.string(),
    date:        z.string(),            // YYYY-MM-DD — Python genera strings
    description: z.string(),
    keywords:    z.array(z.string()).optional(),
    category:    z.string().optional(),
    image:       z.string().optional(),
    amazon_link: z.string().optional(),
    tags:        z.array(z.string()).optional(),
    readTime:    z.number().optional(),
    featured:    z.boolean().default(false),
  }),
});

export const collections = { blog };
