<template>
  <div class="skeleton-list">
    <div v-for="i in count" :key="i" class="skeleton-list__item">
      <div class="skeleton-list__cover skeleton-pulse"></div>
      <div class="skeleton-list__body">
        <div class="skeleton-pulse skeleton-pulse--title"></div>
        <div class="skeleton-pulse skeleton-pulse--text"></div>
        <div class="skeleton-pulse skeleton-pulse--text skeleton-pulse--short"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  count?: number
}>()
</script>

<style scoped>
.skeleton-list {
  display: grid;
  gap: 18px;
}

.skeleton-list__item {
  display: grid;
  gap: 16px;
  grid-template-columns: 180px minmax(0, 1fr);
  border: 1px solid rgba(126, 84, 60, 0.12);
  border-radius: 28px;
  background: rgba(255, 252, 249, 0.8);
  padding: 18px;
}

.skeleton-list__cover {
  min-height: 220px;
  border-radius: 22px;
  background: linear-gradient(
    90deg,
    rgba(200, 180, 160, 0.15) 25%,
    rgba(200, 180, 160, 0.3) 50%,
    rgba(200, 180, 160, 0.15) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

.skeleton-list__body {
  display: grid;
  gap: 14px;
  align-content: center;
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

@media (max-width: 720px) {
  .skeleton-list__item {
    grid-template-columns: 1fr;
  }

  .skeleton-list__cover {
    min-height: 160px;
  }
}
</style>
