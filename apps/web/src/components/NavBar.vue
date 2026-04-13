<template>
  <nav
    class="fixed top-0 left-0 right-0 z-50 bg-white shadow-sm transition-transform duration-300"
    :class="isVisible ? 'translate-y-0' : '-translate-y-full'"
  >
    <div class="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
      <!-- Logo -->
      <router-link to="/" class="flex items-center space-x-2">
        <div class="w-8 h-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-sm">AI</span>
        </div>
        <span class="text-lg font-bold text-gray-900">AI小说</span>
      </router-link>

      <!-- 导航链接 -->
      <div class="hidden md:flex items-center space-x-6">
        <router-link to="/" class="text-sm text-gray-600 hover:text-indigo-600 transition-colors">首页</router-link>
        <router-link to="/rank" class="text-sm text-gray-600 hover:text-indigo-600 transition-colors">排行榜</router-link>
        <router-link to="/" class="text-sm text-gray-600 hover:text-indigo-600 transition-colors">全本</router-link>
        <router-link to="/" class="text-sm text-gray-600 hover:text-indigo-600 transition-colors">免费</router-link>
        <router-link to="/author" class="text-sm text-gray-600 hover:text-indigo-600 transition-colors">作家专区</router-link>
      </div>

      <!-- 搜索和用户 -->
      <div class="flex items-center space-x-3">
        <div class="relative hidden sm:block">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索小说..."
            class="w-48 h-8 pl-8 pr-3 text-sm border border-gray-200 rounded-full focus:outline-none focus:border-indigo-500"
            @keyup.enter="handleSearch"
          />
          <svg class="absolute left-2.5 top-2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center cursor-pointer">
          <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useScroll } from '@/composables/useScroll'

defineProps<{
  isVisible: boolean
}>()

const searchQuery = ref('')

function handleSearch() {
  // 搜索逻辑
  console.log('搜索:', searchQuery.value)
}
</script>
