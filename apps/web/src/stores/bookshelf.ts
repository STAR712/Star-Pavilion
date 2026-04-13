import { defineStore } from 'pinia'
import { getBookshelf, addToBookshelf as apiAdd, removeFromBookshelf as apiRemove, updateProgress as apiUpdateProgress } from '@/api'

export const useBookshelfStore = defineStore('bookshelf', {
  state: () => ({
    books: [] as any[],
    loading: false
  }),
  actions: {
    async fetchBookshelf() {
      this.loading = true
      try {
        const { data } = await getBookshelf()
        this.books = data
      } finally {
        this.loading = false
      }
    },
    async addBook(bookId: number) {
      await apiAdd(bookId)
      await this.fetchBookshelf()
    },
    async removeBook(bookId: number) {
      await apiRemove(bookId)
      await this.fetchBookshelf()
    },
    async updateProgress(bookId: number, chapter: number, progress: number) {
      await apiUpdateProgress(bookId, chapter, progress)
    }
  },
  persist: true
})
