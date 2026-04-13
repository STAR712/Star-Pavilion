import { defineStore } from 'pinia'

export const useReaderStore = defineStore('reader', {
  state: () => ({
    currentBookId: null as number | null,
    currentChapter: 1,
    fontSize: 18,
    theme: 'light' as 'light' | 'dark' | 'sepia',
    chatHistory: [] as Array<{role: string; content: string}>
  }),
  actions: {
    setBook(bookId: number) {
      this.currentBookId = bookId
      this.currentChapter = 1
    },
    setChapter(chapter: number) {
      this.currentChapter = chapter
    },
    toggleTheme() {
      const themes = ['light', 'dark', 'sepia'] as const
      const idx = themes.indexOf(this.theme)
      this.theme = themes[(idx + 1) % themes.length]
    },
    addChatMessage(role: string, content: string) {
      this.chatHistory.push({ role, content })
    },
    clearChat() {
      this.chatHistory = []
    }
  },
  persist: true
})
