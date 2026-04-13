<template>
  <!-- 悬浮按钮 -->
  <div
    v-if="!isOpen"
    class="fixed bottom-24 right-6 w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full shadow-lg flex items-center justify-center cursor-pointer hover:scale-110 transition-transform z-40"
    @click="isOpen = true"
  >
    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
    </svg>
  </div>

  <!-- 对话面板 -->
  <Transition name="slide">
    <div
      v-if="isOpen"
      class="fixed bottom-24 right-6 w-80 sm:w-96 bg-white rounded-2xl shadow-2xl flex flex-col z-40 overflow-hidden"
      style="height: 500px;"
    >
      <!-- 面板头部 -->
      <div class="bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-3 flex items-center justify-between flex-shrink-0">
        <div class="flex items-center space-x-2">
          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
          </svg>
          <span class="text-white font-medium">AI 阅读助手</span>
        </div>
        <button
          class="text-white/80 hover:text-white transition-colors"
          @click="isOpen = false"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- 消息列表 -->
      <div ref="messageListRef" class="flex-1 overflow-y-auto p-4 space-y-3">
        <div v-if="messages.length === 0" class="text-center text-gray-400 text-sm mt-20">
          <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <p>你好！我是AI阅读助手</p>
          <p class="mt-1">可以问我关于小说的任何问题</p>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="flex"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[80%] px-3 py-2 rounded-xl text-sm leading-relaxed"
            :class="
              msg.role === 'user'
                ? 'bg-indigo-500 text-white rounded-br-sm'
                : 'bg-gray-100 text-gray-800 rounded-bl-sm'
            "
          >
            <p class="whitespace-pre-wrap">{{ msg.content }}</p>
          </div>
        </div>

        <!-- 流式输出中的消息 -->
        <div v-if="isStreaming" class="flex justify-start">
          <div class="max-w-[80%] px-3 py-2 rounded-xl rounded-bl-sm bg-gray-100 text-gray-800 text-sm leading-relaxed">
            <p class="whitespace-pre-wrap">{{ streamingContent }}<span class="animate-pulse">|</span></p>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="border-t border-gray-100 p-3 flex-shrink-0">
        <!-- 检索范围开关 -->
        <div class="flex items-center justify-between mb-2 px-1">
          <span class="text-xs text-gray-500">检索范围</span>
          <div class="flex items-center space-x-2">
            <span class="text-xs" :class="searchAll ? 'text-gray-400' : 'text-indigo-500 font-medium'">当前及之前</span>
            <button
              class="relative w-9 h-5 rounded-full transition-colors duration-200"
              :class="searchAll ? 'bg-indigo-500' : 'bg-gray-300'"
              @click="searchAll = !searchAll"
              :disabled="isStreaming"
            >
              <span
                class="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200"
                :class="searchAll ? 'translate-x-4' : 'translate-x-0.5'"
              />
            </button>
            <span class="text-xs" :class="searchAll ? 'text-indigo-500 font-medium' : 'text-gray-400'">全部章节</span>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <input
            v-model="inputText"
            type="text"
            placeholder="输入你的问题..."
            class="flex-1 h-9 px-3 text-sm border border-gray-200 rounded-full focus:outline-none focus:border-indigo-500"
            :disabled="isStreaming"
            @keyup.enter="sendMessage"
          />
          <button
            class="w-9 h-9 bg-indigo-500 text-white rounded-full flex items-center justify-center hover:bg-indigo-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            :disabled="!inputText.trim() || isStreaming"
            @click="sendMessage"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { streamChat } from '@/api'

const props = defineProps<{
  bookId?: number
  chapterId?: number
}>()

const isOpen = ref(false)
const inputText = ref('')
const messages = ref<Array<{ role: string; content: string }>>([])
const isStreaming = ref(false)
const streamingContent = ref('')
const messageListRef = ref<HTMLElement | null>(null)
const searchAll = ref(true)

function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  scrollToBottom()

  isStreaming.value = true
  streamingContent.value = ''

  try {
    const response = await streamChat(messages.value, props.bookId, props.chapterId, searchAll.value)
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      messages.value.push({ role: 'assistant', content: '抱歉，对话服务暂时不可用。' })
      isStreaming.value = false
      return
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const text = decoder.decode(value, { stream: true })
      const lines = text.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue
          try {
            const parsed = JSON.parse(data)
            if (parsed.error) {
              streamingContent.value += `\n[错误] ${parsed.error}`
            } else if (parsed.content) {
              streamingContent.value += parsed.content
            }
          } catch {
            // 忽略解析错误
          }
        }
      }
      scrollToBottom()
    }

    messages.value.push({ role: 'assistant', content: streamingContent.value })
    streamingContent.value = ''
  } catch (error) {
    messages.value.push({ role: 'assistant', content: '抱歉，网络连接出现问题，请稍后重试。' })
  } finally {
    isStreaming.value = false
    scrollToBottom()
  }
}

watch(() => [props.bookId, props.chapterId], () => {
  // 当书籍或章节变化时，清空对话
  messages.value = []
})
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
</style>
