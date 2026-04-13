import type { Directive } from 'vue'

export const vLazyLoad: Directive = {
  mounted(el: HTMLImageElement, binding) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          el.src = binding.value
          observer.unobserve(el)
        }
      })
    })
    observer.observe(el)
    el.src = '' // placeholder
  }
}
