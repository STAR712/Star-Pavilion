import { ref, onMounted, onUnmounted } from 'vue'

export function useScroll(threshold = 100) {
  const isVisible = ref(true)
  let lastScrollY = 0
  let ticking = false

  const handleScroll = () => {
    if (ticking) return
    ticking = true
    requestAnimationFrame(() => {
      const currentScrollY = window.scrollY
      isVisible.value = currentScrollY < lastScrollY || currentScrollY < threshold
      lastScrollY = currentScrollY
      ticking = false
    })
  }

  onMounted(() => window.addEventListener('scroll', handleScroll, { passive: true }))
  onUnmounted(() => window.removeEventListener('scroll', handleScroll))

  return { isVisible }
}
