/// <reference types="vitest/config" />
import mdx from '@mdx-js/rollup'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { mdxOptions } from './src/features/post/mdxOptions.ts'

const API_URL = process.env.API_URL ?? `http://127.0.0.1:${process.env.API_PORT ?? 8000}`
const WEB_PORT = Number(process.env.WEB_PORT ?? 5173)

export default defineConfig({
  plugins: [
    {
      enforce: 'pre',
      ...mdx(mdxOptions),
    },
    react({ include: /\.(mdx|tsx?|jsx?)$/ }),
  ],
  server: {
    port: WEB_PORT,
    strictPort: true,
    proxy: { '/api': { target: API_URL, changeOrigin: true } },
  },
  preview: { port: WEB_PORT, strictPort: true },
  build: {
    target: 'esnext', // top-level await in the Shiki highlighter setup
    rollupOptions: {
      output: {
        // MUI core + Emotion change less often than app code, so they get their own long-cached chunk.
        // MUI X (date pickers) is left out so it stays in the lazy page chunks that use it.
        manualChunks: (id) => (/node_modules\/(@mui\/(?!x-)|@emotion\/)/.test(id) ? 'mui' : undefined),
      },
    },
  },
  test: { environment: 'jsdom', setupFiles: ['./src/test/setup.ts'], testTimeout: 20_000 },
})
