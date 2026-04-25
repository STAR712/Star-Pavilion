import { useToastStore } from '@/stores/toast'

export function useToast() {
  const toastStore = useToastStore()
  return {
    success: (msg: string) => toastStore.success(msg),
    error: (msg: string) => toastStore.error(msg),
    warning: (msg: string) => toastStore.warning(msg),
    info: (msg: string) => toastStore.info(msg),
  }
}
