<script setup lang="ts">
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const showTabbar = computed(() => {
  const routesWithTabbar = ['home', 'expenses', 'statistics', 'profile']
  return routesWithTabbar.includes(String(route.name ?? ''))
})

watch(() => auth.token, (val) => {
  if (!val) router.push('/login')
})
</script>

<template>
  <NotifyBar />
  <router-view />
  <van-tabbar v-if="showTabbar" route placeholder data-testid="app-tabbar">
    <van-tabbar-item name="home" icon="home-o" to="/">首页</van-tabbar-item>
    <van-tabbar-item name="expenses" icon="balance-o" to="/expenses">记账</van-tabbar-item>
    <van-tabbar-item name="statistics" icon="chart-trending-o" to="/statistics">统计</van-tabbar-item>
    <van-tabbar-item name="profile" icon="user-o" to="/profile">我的</van-tabbar-item>
  </van-tabbar>
</template>
