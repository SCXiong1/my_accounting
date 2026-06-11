import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { VantResolver } from 'unplugin-vue-components/resolvers'
import { VitePWA } from 'vite-plugin-pwa'

const isE2E = process.env.E2E_TEST === 'true'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router', 'pinia'],
      resolvers: [
        (name: string) => {
          if (name.startsWith('show') || name.startsWith('close')) {
            return { from: 'vant' }
          }
        },
      ],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [
        VantResolver({ importStyle: true }),
      ],
      dts: 'src/components.d.ts',
    }),
    ...(isE2E ? [] : [VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: '个人记账',
        short_name: '记账',
        description: '个人支出记账应用',
        theme_color: '#1989fa',
        background_color: '#f7f8fa',
        display: 'standalone',
        orientation: 'portrait',
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg}'],
      },
    })]),
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
})
