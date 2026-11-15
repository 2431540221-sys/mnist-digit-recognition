<template>
  <div v-if="error" class="error" role="alert">
    <AppIcon name="alert" :size="16" />
    <span>{{ error }}</span>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import { usePredict } from '../composables/usePredict.js'
const { error } = usePredict()
</script>

<style scoped>
.error {
  margin: 12px 0;
  padding: 10px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 12px;
  color: #f87171;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  backdrop-filter: blur(8px);
}
</style>
