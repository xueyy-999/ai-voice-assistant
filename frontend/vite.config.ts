import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5174,
    strictPort: false,
    host: true
  },
  build: {
    outDir: 'dist/renderer',
    emptyOutDir: true
  }
})

