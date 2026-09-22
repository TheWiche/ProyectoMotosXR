import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  publicDir: 'public',
  server: {
    port: 5173,
    host: true,
    open: false,
    cors: true,
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
  },
});
