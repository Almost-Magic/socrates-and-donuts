import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/socrates-and-donuts/',
  server: {
    port: 5173,
  },
});
