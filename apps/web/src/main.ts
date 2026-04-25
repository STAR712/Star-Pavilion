import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useToastStore } from './stores/toast'
import './style.css'

const app = createApp(App)
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)

// ===== 全局错误处理 =====
app.config.errorHandler = (err, instance, info) => {
  const message = err instanceof Error ? err.message : '未知错误'
  console.error(`[Vue Error] ${info}:`, err)
  // Toast 需要在 pinia 初始化后使用
  try {
    const toastStore = useToastStore()
    toastStore.error(`应用错误: ${message}`)
  } catch {
    // pinia 可能还未就绪
  }
}

window.addEventListener('unhandledrejection', (event) => {
  console.error('[Unhandled Promise]:', event.reason)
  try {
    const toastStore = useToastStore()
    toastStore.error('网络请求异常，请稍后重试')
  } catch {
    // pinia 可能还未就绪
  }
})

useAuthStore(pinia).hydrateSession().finally(() => {
  app.mount('#app')
})
