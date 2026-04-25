<template>
  <div class="chat-root">
    <button v-if="!panelOpen" class="chat-launch" @click="panelOpen = true">
      <span class="chat-launch__icon">AI</span>
      <span class="chat-launch__text">边读边聊</span>
    </button>

    <Teleport to="body">
      <Transition name="chat-modal">
        <div v-if="panelOpen" class="chat-layer">
          <button
            class="chat-backdrop"
            aria-label="关闭 AI 助手"
            @click="panelOpen = false"
          ></button>

          <section class="chat-card" role="dialog" aria-label="AI 阅读助手">
            <header class="chat-card__header">
              <div class="chat-card__heading">
                <p class="chat-card__eyebrow">AI READING COPILOT</p>
                <h3>{{ panelTitle }}</h3>
                <p class="chat-card__subtitle">{{ panelSubtitle }}</p>
              </div>

              <div class="chat-card__header-actions">
                <button
                  v-if="authStore.isAuthenticated && conversationList.length > 0"
                  class="chat-card__history-btn"
                  @click="showConversationList = !showConversationList"
                >
                  历史
                </button>
                <button class="chat-card__close" @click="panelOpen = false">
                  收起
                </button>
              </div>
            </header>

            <div ref="messageViewport" class="chat-card__messages">
              <!-- 对话历史列表 -->
              <div v-if="showConversationList" class="chat-history-panel">
                <div class="chat-history-panel__header">
                  <strong>对话历史</strong>
                  <button class="chat-history-panel__new" @click="startNewConversation">新建对话</button>
                </div>
                <div v-if="conversationList.length === 0" class="chat-history-panel__empty">
                  暂无历史对话
                </div>
                <button
                  v-for="conv in conversationList"
                  :key="conv.id"
                  class="chat-history-panel__item"
                  :class="{ 'chat-history-panel__item--active': conv.id === conversationId }"
                  @click="loadConversation(conv.id)"
                >
                  <div>
                    <strong>{{ conv.name }}</strong>
                    <small>{{ conv.timestamp }}</small>
                  </div>
                  <span class="chat-history-panel__delete" @click.stop="handleDeleteConversation(conv.id)">&times;</span>
                </button>
              </div>

              <div v-if="isLoadingHistory" class="chat-empty">
                <p>正在加载对话历史...</p>
              </div>

              <div v-else-if="messages.length === 0 && !isStreaming && !showConversationList" class="chat-empty">
                <p class="chat-empty__title">问剧情、人物动机、伏笔，或者让助手帮你梳理这一章。</p>
                <p class="chat-empty__note">是否允许剧透由下方开关决定，关闭时会优先限制在当前阅读进度内回答。</p>
              </div>

              <div
                v-for="(message, index) in renderedMessages"
                :key="`${message.role}-${index}`"
                class="chat-row"
                :class="{ 'chat-row--user': message.role === 'user' }"
              >
                <div
                  class="chat-bubble"
                  :class="message.role === 'user' ? 'chat-bubble--user' : 'chat-bubble--assistant'"
                  v-html="message.html"
                ></div>
              </div>

              <div v-if="isStreaming" class="chat-row">
                <div class="chat-bubble chat-bubble--assistant">
                  <div v-html="streamingHtml"></div>
                  <span class="chat-bubble__typing"></span>
                </div>
              </div>
            </div>

            <footer class="chat-card__footer">
              <label class="spoiler-switch">
                <div>
                  <strong>是否剧透未来章节</strong>
                  <p>{{ searchAll ? '允许助手引用全书剧情线索' : '仅结合当前进度与已读上下文回答' }}</p>
                </div>
                <button
                  type="button"
                  class="spoiler-switch__track"
                  :class="{ 'spoiler-switch__track--on': searchAll }"
                  :aria-pressed="searchAll"
                  @click="searchAll = !searchAll"
                >
                  <span></span>
                </button>
              </label>

              <form class="chat-input" @submit.prevent="sendMessage">
                <textarea
                  v-model="inputText"
                  rows="3"
                  placeholder="输入你想问的问题，Shift + Enter 换行"
                  @keydown="handleInputKeydown"
                ></textarea>
                <button class="chat-input__submit" :disabled="isStreaming || !inputText.trim()">
                  {{ isStreaming ? '生成中…' : '发送' }}
                </button>
              </form>
            </footer>
          </section>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { streamChat, createConversation, getConversation, updateConversation, getConversations, deleteConversation } from '@/api'
import { renderMarkdown } from '@/utils/markdown'
import { useAuthStore } from '@/stores/auth'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

const props = withDefaults(defineProps<{
  bookId?: number
  chapterId?: number
  bookTitle?: string
  chapterTitle?: string
  open?: boolean
}>(), {
  bookTitle: '',
  chapterTitle: '',
  open: undefined,
})

const emit = defineEmits<{
  'update:open': [boolean]
}>()

const authStore = useAuthStore()

const internalOpen = ref(false)
const inputText = ref('')
const messages = ref<ChatMessage[]>([])
const isStreaming = ref(false)
const streamingContent = ref('')
const searchAll = ref(false)
const parserBuffer = ref('')
const messageViewport = ref<HTMLElement | null>(null)
const conversationId = ref<number | null>(null)
const isLoadingHistory = ref(false)
const conversationList = ref<Array<{ id: number; name: string; book_id: number | null; timestamp: string }>>([])
const showConversationList = ref(false)

const panelOpen = computed({
  get: () => props.open ?? internalOpen.value,
  set: (value: boolean) => {
    internalOpen.value = value
    emit('update:open', value)
  },
})

const panelTitle = computed(() => 'AI 阅读助手')
const panelSubtitle = computed(() => {
  if (props.bookTitle && props.chapterTitle) {
    return `${props.bookTitle} · ${props.chapterTitle}`
  }
  if (props.bookTitle) {
    return props.bookTitle
  }
  return '围绕当前阅读内容随时聊'
})

const renderedMessages = computed(() =>
  messages.value.map((message) => ({
    ...message,
    html: renderMarkdown(message.content),
  })),
)

const streamingHtml = computed(() =>
  renderMarkdown(`${streamingContent.value || '正在整理回答'}\n\n...`),
)

function scrollToBottom() {
  nextTick(() => {
    if (messageViewport.value) {
      messageViewport.value.scrollTop = messageViewport.value.scrollHeight
    }
  })
}

function handleInputKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

function pushAssistantMessage(content: string) {
  const value = content.trim() || '我暂时没有整理出有效回答，你可以换个角度继续问我。'
  messages.value.push({ role: 'assistant', content: value })
}

function consumeSseChunk(chunk: string) {
  parserBuffer.value += chunk
  const blocks = parserBuffer.value.split('\n\n')
  parserBuffer.value = blocks.pop() || ''

  for (const block of blocks) {
    const line = block
      .split('\n')
      .find((item) => item.startsWith('data: '))

    if (!line) continue

    const data = line.slice(6).trim()
    if (data === '[DONE]') continue

    try {
      const parsed = JSON.parse(data)
      if (parsed.error) {
        streamingContent.value += `\n[错误] ${parsed.error}`
      } else if (parsed.content) {
        streamingContent.value += parsed.content
      }
    } catch {
      // 等待后续 chunk 补齐 JSON
    }
  }
}

/** 确保有活跃的 conversation，没有则创建 */
async function ensureConversation(): Promise<number | null> {
  if (conversationId.value) return conversationId.value
  if (!authStore.isAuthenticated) return null

  try {
    const { data } = await createConversation({
      book_id: props.bookId,
      chapter_id: props.chapterId,
      name: props.bookTitle ? `${props.bookTitle} 对话` : '新对话',
    })
    conversationId.value = data.id
    return data.id
  } catch {
    return null
  }
}

/** 加载对话历史 */
async function loadConversation(convId: number) {
  isLoadingHistory.value = true
  try {
    const { data } = await getConversation(convId)
    conversationId.value = data.id
    messages.value = (data.messages || []).map((m: any) => ({
      role: m.role,
      content: m.content,
    }))
    showConversationList.value = false
    scrollToBottom()
  } catch {
    // 加载失败，保持当前状态
  } finally {
    isLoadingHistory.value = false
  }
}

/** 加载对话列表 */
async function loadConversationList() {
  if (!authStore.isAuthenticated) return
  try {
    const params: any = {}
    if (props.bookId) params.book_id = props.bookId
    const { data } = await getConversations(params)
    conversationList.value = data || []
  } catch {
    conversationList.value = []
  }
}

/** 保存消息到后端 */
async function saveMessages() {
  if (!conversationId.value) return
  try {
    await updateConversation(conversationId.value, {
      messages: messages.value.map((m) => ({ role: m.role, content: m.content })),
    })
  } catch {
    // 保存失败不影响用户体验
  }
}

/** 新建对话 */
function startNewConversation() {
  conversationId.value = null
  messages.value = []
  streamingContent.value = ''
  parserBuffer.value = ''
  showConversationList.value = false
}

/** 删除对话 */
async function handleDeleteConversation(convId: number) {
  try {
    await deleteConversation(convId)
    if (convId === conversationId.value) {
      startNewConversation()
    }
    await loadConversationList()
  } catch {
    // 删除失败静默处理
  }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return

  panelOpen.value = true
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  streamingContent.value = ''
  parserBuffer.value = ''
  isStreaming.value = true
  scrollToBottom()

  // 确保有 conversation
  const convId = await ensureConversation()

  try {
    const response = await streamChat(
      messages.value,
      props.bookId,
      props.chapterId,
      searchAll.value,
      convId,
    )
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      pushAssistantMessage('抱歉，对话服务暂时不可用。')
      return
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      consumeSseChunk(decoder.decode(value, { stream: true }))
      scrollToBottom()
    }

    if (parserBuffer.value) {
      consumeSseChunk('\n\n')
    }

    pushAssistantMessage(streamingContent.value)
    streamingContent.value = ''

    // 保存消息到后端
    await saveMessages()
  } catch {
    pushAssistantMessage('抱歉，当前网络状态不稳定，请稍后再试。')
  } finally {
    isStreaming.value = false
    parserBuffer.value = ''
    scrollToBottom()
  }
}

// 打开面板时加载对话列表
watch(panelOpen, (open) => {
  if (open) {
    loadConversationList()
  }
})

watch(
  () => [props.bookId, props.chapterId],
  () => {
    // 切换书籍/章节时，重置对话状态
    startNewConversation()
  },
)

watch(
  () => [messages.value.length, streamingContent.value, panelOpen.value],
  () => {
    if (panelOpen.value) {
      scrollToBottom()
    }
  },
)
</script>

<style scoped>
.chat-root {
  position: relative;
  z-index: 40;
}

.chat-launch {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 45;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(32, 19, 23, 0.94), rgba(140, 63, 44, 0.92));
  padding: 14px 18px;
  color: white;
  box-shadow: 0 18px 38px rgba(82, 31, 20, 0.24);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.chat-launch:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 46px rgba(82, 31, 20, 0.28);
}

.chat-launch__icon {
  display: grid;
  height: 36px;
  width: 36px;
  place-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.chat-launch__text {
  font-size: 14px;
}

.chat-layer {
  position: fixed;
  inset: 0;
  z-index: 60;
  pointer-events: none;
}

.chat-backdrop {
  display: none;
}

.chat-card {
  position: absolute;
  right: 24px;
  bottom: 24px;
  display: grid;
  height: min(78vh, 720px);
  width: min(430px, calc(100vw - 32px));
  grid-template-rows: auto minmax(0, 1fr) auto;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 32px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(252, 247, 244, 0.72)),
    radial-gradient(circle at top right, rgba(250, 205, 185, 0.34), transparent 38%);
  box-shadow: 0 34px 80px rgba(107, 67, 45, 0.22);
  backdrop-filter: blur(30px) saturate(1.2);
  pointer-events: auto;
}

.chat-card__header,
.chat-card__footer {
  padding: 22px 22px 18px;
}

.chat-card__header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid rgba(133, 101, 78, 0.12);
}

.chat-card__heading h3 {
  margin: 8px 0 0;
  font-family: 'Iowan Old Style', 'Songti SC', serif;
  font-size: 30px;
  line-height: 1.06;
  color: #2c1c16;
}

.chat-card__eyebrow {
  font-size: 11px;
  letter-spacing: 0.26em;
  color: #9e6f5b;
}

.chat-card__subtitle {
  margin-top: 10px;
  color: #76594b;
  line-height: 1.6;
}

.chat-card__close {
  border: 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.74);
  padding: 10px 14px;
  color: #7e533f;
}

.chat-card__messages {
  display: grid;
  gap: 16px;
  overflow-y: auto;
  padding: 22px;
}

.chat-empty {
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.66);
  padding: 18px;
  color: #72584c;
}

.chat-empty__title {
  margin: 0;
  line-height: 1.8;
}

.chat-empty__note {
  margin: 12px 0 0;
  font-size: 13px;
  line-height: 1.7;
  color: #977566;
}

.chat-row {
  display: flex;
  justify-content: flex-start;
}

.chat-row--user {
  justify-content: flex-end;
}

.chat-bubble {
  max-width: min(100%, 308px);
  border-radius: 22px;
  padding: 15px 16px;
  line-height: 1.78;
  color: #3d2d27;
}

.chat-bubble--assistant {
  border: 1px solid rgba(124, 91, 68, 0.1);
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 10px 28px rgba(110, 71, 49, 0.08);
}

.chat-bubble--user {
  background: linear-gradient(135deg, #25171a, #8c3f2c);
  color: white;
  box-shadow: 0 12px 32px rgba(89, 41, 28, 0.18);
}

.chat-bubble__typing {
  display: inline-block;
  margin-left: 6px;
  height: 8px;
  width: 8px;
  border-radius: 999px;
  background: #8c3f2c;
  animation: pulse 1s ease-in-out infinite;
}

.chat-card__footer {
  display: grid;
  gap: 16px;
  border-top: 1px solid rgba(133, 101, 78, 0.12);
}

.spoiler-switch {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.62);
  padding: 14px 16px;
}

.spoiler-switch strong {
  display: block;
  color: #2d1c16;
}

.spoiler-switch p {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: #836557;
}

.spoiler-switch__track {
  position: relative;
  flex: none;
  height: 32px;
  width: 60px;
  border: 0;
  border-radius: 999px;
  background: rgba(148, 130, 118, 0.34);
  padding: 4px;
  transition: background 0.25s ease;
}

.spoiler-switch__track span {
  display: block;
  height: 24px;
  width: 24px;
  border-radius: 999px;
  background: white;
  box-shadow: 0 6px 18px rgba(82, 54, 40, 0.16);
  transition: transform 0.25s ease;
}

.spoiler-switch__track--on {
  background: rgba(140, 63, 44, 0.92);
}

.spoiler-switch__track--on span {
  transform: translateX(28px);
}

.chat-input {
  display: grid;
  gap: 12px;
}

.chat-input textarea {
  width: 100%;
  resize: none;
  border: 1px solid rgba(129, 96, 75, 0.14);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.84);
  padding: 16px 18px;
  color: #2d1c16;
  outline: none;
}

.chat-input textarea:focus {
  border-color: rgba(140, 63, 44, 0.28);
}

.chat-input__submit {
  justify-self: end;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(135deg, #201317, #8c3f2c);
  padding: 12px 18px;
  color: white;
}

.chat-input__submit:disabled {
  opacity: 0.6;
}

.chat-modal-enter-active,
.chat-modal-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.chat-modal-enter-from,
.chat-modal-leave-to {
  opacity: 0;
}

.chat-modal-enter-from .chat-card,
.chat-modal-leave-to .chat-card {
  transform: translateY(18px) scale(0.98);
}

.chat-bubble :deep(p:first-child),
.chat-bubble :deep(ul:first-child),
.chat-bubble :deep(blockquote:first-child),
.chat-bubble :deep(pre:first-child),
.chat-bubble :deep(h1:first-child),
.chat-bubble :deep(h2:first-child),
.chat-bubble :deep(h3:first-child),
.chat-bubble :deep(h4:first-child) {
  margin-top: 0;
}

.chat-bubble :deep(p:last-child),
.chat-bubble :deep(ul:last-child),
.chat-bubble :deep(blockquote:last-child),
.chat-bubble :deep(pre:last-child) {
  margin-bottom: 0;
}

.chat-bubble :deep(p) {
  margin: 0 0 10px;
}

.chat-bubble :deep(ul) {
  margin: 0 0 10px;
  padding-left: 18px;
}

.chat-bubble :deep(li + li) {
  margin-top: 6px;
}

.chat-bubble :deep(code) {
  border-radius: 8px;
  background: rgba(44, 28, 22, 0.08);
  padding: 2px 6px;
  font-size: 0.92em;
}

.chat-bubble :deep(pre) {
  overflow-x: auto;
  border-radius: 16px;
  background: rgba(44, 28, 22, 0.08);
  padding: 14px;
}

.chat-bubble :deep(blockquote) {
  margin: 0 0 10px;
  border-left: 3px solid rgba(140, 63, 44, 0.3);
  padding-left: 12px;
  color: inherit;
}

.chat-bubble :deep(a) {
  color: inherit;
}

.chat-bubble :deep(.citation-tag) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-radius: 8px;
  background: rgba(140, 63, 44, 0.08);
  padding: 2px 8px;
  font-size: 0.85em;
  color: #8c3f2c;
  cursor: pointer;
  transition: background 0.2s;
}

.chat-bubble :deep(.citation-tag:hover) {
  background: rgba(140, 63, 44, 0.15);
}

.chat-card__header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-card__history-btn {
  border: 1px solid rgba(126, 84, 60, 0.15);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.6);
  padding: 8px 14px;
  font-size: 13px;
  color: #7e533f;
  cursor: pointer;
}

.chat-history-panel {
  border: 1px solid rgba(126, 84, 60, 0.1);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.6);
  padding: 14px;
  margin-bottom: 12px;
}

.chat-history-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chat-history-panel__header strong {
  font-size: 14px;
  color: #2c1c16;
}

.chat-history-panel__new {
  border: 0;
  border-radius: 999px;
  background: rgba(140, 63, 44, 0.1);
  padding: 6px 12px;
  font-size: 12px;
  color: #8c3f2c;
  cursor: pointer;
}

.chat-history-panel__empty {
  text-align: center;
  padding: 16px;
  color: #977566;
  font-size: 13px;
}

.chat-history-panel__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  border: 0;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.5);
  padding: 10px 12px;
  margin-bottom: 6px;
  text-align: left;
  cursor: pointer;
  transition: background 0.2s;
}

.chat-history-panel__item:hover {
  background: rgba(255, 255, 255, 0.8);
}

.chat-history-panel__item--active {
  background: rgba(140, 63, 44, 0.1);
  border: 1px solid rgba(140, 63, 44, 0.2);
}

.chat-history-panel__item strong {
  display: block;
  font-size: 13px;
  color: #2c1c16;
}

.chat-history-panel__item small {
  font-size: 11px;
  color: #977566;
}

.chat-history-panel__delete {
  font-size: 18px;
  color: #c47a6a;
  cursor: pointer;
  padding: 0 4px;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.35;
  }

  50% {
    opacity: 1;
  }
}

@media (max-width: 1024px) {
  .chat-layer {
    pointer-events: auto;
  }

  .chat-backdrop {
    position: absolute;
    inset: 0;
    display: block;
    border: 0;
    background: rgba(35, 24, 20, 0.2);
  }
}

@media (max-width: 720px) {
  .chat-launch {
    right: 16px;
    bottom: 16px;
    padding: 12px 14px;
  }

  .chat-launch__text {
    display: none;
  }

  .chat-card {
    right: 16px;
    bottom: 16px;
    left: 16px;
    width: auto;
    height: min(76vh, 680px);
  }

  .chat-card__header,
  .chat-card__messages,
  .chat-card__footer {
    padding-left: 18px;
    padding-right: 18px;
  }
}
</style>
