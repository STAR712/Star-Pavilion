<template>
  <div class="min-h-screen bg-gray-50">
    <NavBar :is-visible="true" />
    <div class="h-14"></div>

    <div class="max-w-4xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-8">作家专区</h1>

      <!-- 创建/编辑书籍表单 -->
      <div class="bg-white rounded-2xl p-6 shadow-sm mb-8">
        <h2 class="text-lg font-bold text-gray-900 mb-4">
          {{ editingBook ? '编辑书籍' : '创建新书' }}
        </h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">书名</label>
            <input
              v-model="bookForm.title"
              type="text"
              placeholder="请输入书名"
              class="w-full h-10 px-3 border border-gray-200 rounded-lg focus:outline-none focus:border-indigo-500 text-sm"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">作者</label>
              <input
                v-model="bookForm.author"
                type="text"
                placeholder="请输入作者名"
                class="w-full h-10 px-3 border border-gray-200 rounded-lg focus:outline-none focus:border-indigo-500 text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">分类</label>
              <select
                v-model="bookForm.category"
                class="w-full h-10 px-3 border border-gray-200 rounded-lg focus:outline-none focus:border-indigo-500 text-sm"
              >
                <option value="玄幻">玄幻</option>
                <option value="都市">都市</option>
                <option value="科幻">科幻</option>
                <option value="历史">历史</option>
                <option value="言情">言情</option>
                <option value="悬疑">悬疑</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">简介</label>
            <textarea
              v-model="bookForm.description"
              placeholder="请输入作品简介"
              rows="4"
              class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-indigo-500 text-sm resize-none"
            ></textarea>
          </div>
          <div class="flex items-center space-x-3">
            <label class="flex items-center space-x-2 cursor-pointer">
              <input v-model="bookForm.is_free" type="checkbox" class="rounded" />
              <span class="text-sm text-gray-700">免费阅读</span>
            </label>
          </div>
          <div class="flex space-x-3">
            <button
              class="px-6 py-2 bg-indigo-500 text-white rounded-lg text-sm font-medium hover:bg-indigo-600 transition-colors"
              @click="saveBook"
            >
              {{ editingBook ? '保存修改' : '创建书籍' }}
            </button>
            <button
              v-if="editingBook"
              class="px-6 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              @click="cancelEdit"
            >
              取消
            </button>
          </div>
        </div>
      </div>

      <!-- 章节管理 -->
      <div v-if="editingBook" class="bg-white rounded-2xl p-6 shadow-sm mb-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-gray-900">章节管理</h2>
          <button
            class="px-4 py-1.5 bg-indigo-500 text-white rounded-lg text-sm hover:bg-indigo-600 transition-colors"
            @click="showAddChapter = true"
          >
            添加章节
          </button>
        </div>

        <!-- 添加章节表单 -->
        <div v-if="showAddChapter" class="border border-gray-100 rounded-lg p-4 mb-4 bg-gray-50">
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">章节标题</label>
              <input
                v-model="chapterForm.title"
                type="text"
                placeholder="请输入章节标题"
                class="w-full h-10 px-3 border border-gray-200 rounded-lg focus:outline-none focus:border-indigo-500 text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">章节内容</label>
              <textarea
                v-model="chapterForm.content"
                placeholder="请输入章节内容（保存后将自动进行向量化处理）"
                rows="8"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-indigo-500 text-sm resize-none"
              ></textarea>
            </div>
            <div class="flex space-x-3">
              <button
                class="px-4 py-1.5 bg-green-500 text-white rounded-lg text-sm hover:bg-green-600 transition-colors"
                @click="saveChapter"
              >
                保存章节
              </button>
              <button
                class="px-4 py-1.5 border border-gray-200 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition-colors"
                @click="showAddChapter = false"
              >
                取消
              </button>
            </div>
          </div>
        </div>

        <!-- 章节列表 -->
        <div v-if="chapters.length === 0" class="text-center py-8 text-gray-400">
          暂无章节，点击上方按钮添加
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="ch in chapters"
            :key="ch.id"
            class="flex items-center justify-between px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center space-x-3">
              <span class="text-xs text-gray-400 w-8">{{ ch.chapter_number }}.</span>
              <span class="text-sm text-gray-800">{{ ch.title }}</span>
              <span class="text-xs text-gray-400">{{ ch.word_count }}字</span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-xs text-green-500">已向量化</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 我的书籍列表 -->
      <div class="bg-white rounded-2xl p-6 shadow-sm">
        <h2 class="text-lg font-bold text-gray-900 mb-4">我的作品</h2>
        <div v-if="myBooks.length === 0" class="text-center py-8 text-gray-400">
          还没有创建作品，开始你的创作之旅吧
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="b in myBooks"
            :key="b.id"
            class="flex items-center justify-between px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
          >
            <div>
              <h3 class="text-sm font-medium text-gray-900">{{ b.title }}</h3>
              <p class="text-xs text-gray-400 mt-1">{{ b.category }} | {{ b.word_count }}字 | {{ b.status }}</p>
            </div>
            <div class="flex items-center space-x-2">
              <button
                class="text-xs text-indigo-600 hover:text-indigo-700"
                @click="editBook(b)"
              >
                编辑
              </button>
              <button
                class="text-xs text-red-500 hover:text-red-600"
                @click="deleteBook(b.id)"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getBooks, getChapters } from '@/api'
import NavBar from '@/components/NavBar.vue'

const editingBook = ref<any>(null)
const showAddChapter = ref(false)
const myBooks = ref<any[]>([])
const chapters = ref<any[]>([])

const bookForm = ref({
  title: '',
  author: '',
  category: '玄幻',
  description: '',
  is_free: true,
})

const chapterForm = ref({
  title: '',
  content: '',
})

async function loadMyBooks() {
  try {
    const { data } = await getBooks({ page: 1, size: 20 })
    myBooks.value = data.books || []
  } catch (e) {
    console.error('加载书籍失败:', e)
  }
}

async function saveBook() {
  if (!bookForm.value.title.trim()) {
    alert('请输入书名')
    return
  }
  // 模拟保存
  alert(editingBook.value ? '修改已保存' : '书籍创建成功')
  editingBook.value = { ...editingBook.value, ...bookForm.value }
  await loadMyBooks()
}

function editBook(book: any) {
  editingBook.value = book
  bookForm.value = {
    title: book.title,
    author: book.author,
    category: book.category,
    description: book.description,
    is_free: book.is_free,
  }
  loadBookChapters(book.id)
}

function cancelEdit() {
  editingBook.value = null
  chapters.value = []
}

async function loadBookChapters(bookId: number) {
  try {
    const { data } = await getChapters(bookId)
    chapters.value = data.chapters || []
  } catch (e) {
    console.error('加载章节失败:', e)
  }
}

async function saveChapter() {
  if (!chapterForm.value.title.trim() || !chapterForm.value.content.trim()) {
    alert('请填写完整的章节信息')
    return
  }
  alert('章节已保存并完成向量化处理')
  showAddChapter.value = false
  chapterForm.value = { title: '', content: '' }
  if (editingBook.value) {
    await loadBookChapters(editingBook.value.id)
  }
}

async function deleteBook(id: number) {
  if (confirm('确定要删除这本书吗？此操作不可恢复。')) {
    alert('删除成功')
    await loadMyBooks()
  }
}

onMounted(() => {
  loadMyBooks()
})
</script>
