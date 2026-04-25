import { defineStore } from 'pinia'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastItem {
  id: number
  message: string
  type: ToastType
}

let nextId = 0

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: [] as ToastItem[],
  }),
  actions: {
    show(message: string, type: ToastType = 'info', duration = 3000) {
      const id = nextId++
      this.toasts.push({ id, message, type })
      setTimeout(() => {
        this.remove(id)
      }, duration)
    },
    success(message: string) {
      this.show(message, 'success')
    },
    error(message: string) {
      this.show(message, 'error', 5000)
    },
    warning(message: string) {
      this.show(message, 'warning')
    },
    info(message: string) {
      this.show(message, 'info')
    },
    remove(id: number) {
      const index = this.toasts.findIndex((t) => t.id === id)
      if (index !== -1) {
        this.toasts.splice(index, 1)
      }
    },
  },
})
