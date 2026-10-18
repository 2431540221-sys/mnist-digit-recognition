<template>
  <p v-if="error" class="error" role="alert">
    <AppIcon name="alert" :size="16" />
    <span>{{ error }}</span>
  </p>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import { usePredict } from '../composables/usePredict.js'
const { error } = usePredict()
</script>

<style scoped>
.error {
  margin: 0 0 14px;
  padding: 10px 14px;
  background: #fef2f2;
  border: 2px solid #fecaca;
  border-radius: 12px;
  color: #b91c1c;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>