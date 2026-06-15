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
  optimizeDeps: {
    include: [
      'vant/es/button/style/index',
      'vant/es/cell/style/index',
      'vant/es/cell-group/style/index',
      'vant/es/checkbox/style/index',
      'vant/es/checkbox-group/style/index',
      'vant/es/date-picker/style/index',
      'vant/es/dialog/style/index',
      'vant/es/divider/style/index',
      'vant/es/field/style/index',
      'vant/es/form/style/index',
      'vant/es/grid/style/index',
      'vant/es/grid-item/style/index',
      'vant/es/icon/style/index',
      'vant/es/list/style/index',
      'vant/es/loading/style/index',
      'vant/es/nav-bar/style/index',
      'vant/es/picker/style/index',
      'vant/es/popup/style/index',
      'vant/es/pull-refresh/style/index',
      'vant/es/search/style/index',
      'vant/es/swipe-cell/style/index',
      'vant/es/tabbar/style/index',
      'vant/es/tabbar-item/style/index',
      'vant/es/tag/style/index',
      'vant/es/toast/style/index',
      'vant/es/notify/style/index',
      'echarts',
    ],
  },
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
