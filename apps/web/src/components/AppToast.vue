<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast-item"
        :class="`toast-item--${toast.type || 'info'}`"
      >
        <span class="toast-item__icon">{{ iconMap[toast.type || 'info'] }}</span>
        <p class="toast-item__message">{{ toast.message }}</p>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const toasts = computed(() => toastStore.toasts)

const iconMap: Record<string, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  display: grid;
  gap: 10px;
  pointer-events: none;
}

.toast-item {
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 16px;
  background: rgba(255, 252, 249, 0.94);
  padding: 14px 18px;
  box-shadow: 0 12px 32px rgba(90, 48, 28, 0.12);
  backdrop-filter: blur(16px);
  pointer-events: auto;
  min-width: 260px;
  max-width: 400px;
  border: 1px solid rgba(126, 84, 60, 0.1);
}

.toast-item--success {
  border-left: 4px solid #4caf50;
}

.toast-item--error {
  border-left: 4px solid #e53935;
}

.toast-item--warning {
  border-left: 4px solid #ff9800;
}

.toast-item--info {
  border-left: 4px solid #2196f3;
}

.toast-item__icon {
  flex: none;
  height: 28px;
  width: 28px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  color: white;
}

.toast-item--success .toast-item__icon {
  background: #4caf50;
}

.toast-item--error .toast-item__icon {
  background: #e53935;
}

.toast-item--warning .toast-item__icon {
  background: #ff9800;
}

.toast-item--info .toast-item__icon {
  background: #2196f3;
}

.toast-item__message {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #2c1c16;
}

.toast-enter-active {
  transition: all 0.3s ease;
}

.toast-leave-active {
  transition: all 0.25s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>
