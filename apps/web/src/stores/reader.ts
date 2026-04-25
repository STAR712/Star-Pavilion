import { defineStore } from 'pinia'

export const useReaderStore = defineStore('reader', {
  state: () => ({
    currentBookId: null as number | null,
    currentChapter: 1,
    fontSize: 18,
    theme: 'paper' as 'paper' | 'night' | 'eye',
    sidebarOpen: true,
  }),
  actions: {
    setBook(bookId: number) {
      this.currentBookId = bookId
    },
    setChapter(chapter: number) {
      this.currentChapter = chapter
    },
    setTheme(theme: 'paper' | 'night' | 'eye') {
      this.theme = theme
    },
    toggleTheme() {
      const themes = ['paper', 'eye', 'night'] as const
      const idx = themes.indexOf(this.theme)
      this.theme = themes[(idx + 1) % themes.length]
    },
    setSidebarOpen(value: boolean) {
      this.sidebarOpen = value
    },
    increaseFontSize() {
      this.fontSize = Math.min(this.fontSize + 2, 30)
    },
    decreaseFontSize() {
      this.fontSize = Math.max(this.fontSize - 2, 14)
    },
  },
  persist: true
})
