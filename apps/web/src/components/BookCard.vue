<template>
  <div
    class="book-card bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
    @click="$router.push(`/book/${book.id}`)"
  >
    <div class="relative w-full aspect-[3/4] bg-gray-200 overflow-hidden">
      <img
        v-if="book.cover_url"
        :src="book.cover_url"
        :alt="book.title"
        class="w-full h-full object-cover"
        loading="lazy"
      />
      <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600">
        <span class="text-white text-2xl font-bold px-4 text-center leading-tight">{{ book.title }}</span>
      </div>
      <span
        v-if="book.category"
        class="absolute top-2 left-2 bg-black/50 text-white text-xs px-2 py-0.5 rounded"
      >
        {{ book.category }}
      </span>
      <span
        v-if="book.status === '已完结'"
        class="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-0.5 rounded"
      >
        完结
      </span>
    </div>
    <div class="p-3">
      <h3 class="text-sm font-medium text-gray-900 truncate">{{ book.title }}</h3>
      <p class="text-xs text-gray-500 mt-1 truncate">{{ book.author }}</p>
      <div class="flex items-center justify-between mt-2">
        <span class="text-xs text-gray-400">{{ formatWordCount(book.word_count) }}</span>
        <span class="text-xs text-red-500">{{ formatReadCount(book.read_count) }}阅读</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  book: {
    id: number
    title: string
    author: string
    cover_url?: string
    category?: string
    word_count?: number
    read_count?: number
    status?: string
  }
}>()

function formatWordCount(count?: number): string {
  if (!count) return '0字'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万字'
  return count + '字'
}

function formatReadCount(count?: number): string {
  if (!count) return '0'
  if (count >= 10000) return (count / 10000).toFixed(1) + '万'
  return count.toString()
}
</script>
