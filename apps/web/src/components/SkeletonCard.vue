<template>
  <div class="skeleton-card" :class="{ 'skeleton-card--horizontal': horizontal }">
    <div class="skeleton-card__cover skeleton-pulse"></div>
    <div v-if="horizontal" class="skeleton-card__body">
      <div class="skeleton-pulse skeleton-pulse--title"></div>
      <div class="skeleton-pulse skeleton-pulse--text"></div>
      <div class="skeleton-pulse skeleton-pulse--text skeleton-pulse--short"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  horizontal?: boolean
}>()
</script>

<style scoped>
.skeleton-card {
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 28px;
  background: rgba(255, 252, 249, 0.8);
  overflow: hidden;
}

.skeleton-card--horizontal {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
}

.skeleton-card__cover {
  min-height: 420px;
  background: linear-gradient(
    90deg,
    rgba(200, 180, 160, 0.15) 25%,
    rgba(200, 180, 160, 0.3) 50%,
    rgba(200, 180, 160, 0.15) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-card--horizontal .skeleton-card__cover {
  min-height: 100%;
}

.skeleton-card__body {
  display: grid;
  gap: 14px;
  align-content: center;
  padding: 24px;
}

.skeleton-pulse--title {
  height: 28px;
  width: 60%;
  border-radius: 14px;
  background: linear-gradient(
    90deg,
    rgba(200, 180, 160, 0.15) 25%,
    rgba(200, 180, 160, 0.3) 50%,
    rgba(200, 180, 160, 0.15) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-pulse--text {
  height: 16px;
  width: 90%;
  border-radius: 12px;
  background: linear-gradient(
    90deg,
    rgba(200, 180, 160, 0.15) 25%,
    rgba(200, 180, 160, 0.3) 50%,
    rgba(200, 180, 160, 0.15) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-pulse--short {
  width: 50%;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 1080px) {
  .skeleton-card--horizontal {
    grid-template-columns: 1fr;
  }

  .skeleton-card--horizontal .skeleton-card__cover {
    min-height: 280px;
  }
}
</style>
