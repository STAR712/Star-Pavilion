import { defineStore } from 'pinia'
import { getAccessToken, getBookshelf, addToBookshelf as apiAdd, removeFromBookshelf as apiRemove, updateProgress as apiUpdateProgress } from '@/api'

export const useBookshelfStore = defineStore('bookshelf', {
  state: () => ({
    books: [] as any[],
    loading: false,
    source: 'api' as 'api' | 'local'
  }),
  actions: {
    clearBooks() {
      this.books = []
      this.source = 'local'
    },
    async fetchBookshelf() {
      if (!getAccessToken()) {
        this.clearBooks()
        return
      }
      this.loading = true
      try {
        const { data } = await getBookshelf()
        this.books = data
        this.source = 'api'
      } catch {
        this.source = 'local'
      } finally {
        this.loading = false
      }
    },
    async addBook(bookId: number, fallback?: Partial<any>) {
      if (!getAccessToken()) {
        throw new Error('AUTH_REQUIRED')
      }
      try {
        await apiAdd(bookId)
        await this.fetchBookshelf()
        return
      } catch {
        if (this.books.some((book) => Number(book.book_id) === bookId)) return
        this.source = 'local'
        this.books.unshift({
          id: `local-${bookId}`,
          book_id: bookId,
          book_title: fallback?.book_title || fallback?.title || '未命名小说',
          book_author: fallback?.book_author || fallback?.author || '未知作者',
          book_cover_url: fallback?.book_cover_url || fallback?.cover_url || '',
          current_chapter: 1,
          progress: 0,
          added_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      }
    },
    async removeBook(bookId: number) {
      if (!getAccessToken()) {
        throw new Error('AUTH_REQUIRED')
      }
      try {
        await apiRemove(bookId)
        await this.fetchBookshelf()
      } catch {
        this.source = 'local'
        this.books = this.books.filter((book) => Number(book.book_id) !== bookId)
      }
    },
    async updateProgress(bookId: number, chapter: number, progress: number, fallback?: Partial<any>) {
      if (!getAccessToken()) {
        return
      }
      try {
        await apiUpdateProgress(bookId, chapter, progress)
      } catch {
        this.source = 'local'
        const target = this.books.find((book) => Number(book.book_id) === bookId)
        if (target) {
          target.current_chapter = chapter
          target.progress = progress
          target.updated_at = new Date().toISOString()
          return
        }

        this.books.unshift({
          id: `local-${bookId}`,
          book_id: bookId,
          book_title: fallback?.book_title || fallback?.title || '未命名小说',
          book_author: fallback?.book_author || fallback?.author || '未知作者',
          book_cover_url: fallback?.book_cover_url || fallback?.cover_url || '',
          current_chapter: chapter,
          progress,
          added_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      }
    }
  },
  persist: true
})
