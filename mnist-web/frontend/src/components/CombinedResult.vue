<template>
  <div v-if="number" class="combined">
    <span class="combined__label">Số hoàn chỉnh</span>
    <strong class="combined__digits">{{ number }}</strong>
    <AppIcon name="sparkles" :size="20" class="combined__sparkle" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { usePredict } from '../composables/usePredict.js'

const { combinedNumber } = usePredict()
const number = computed(() => combinedNumber.value)
</script>

<style scoped>
.combined {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 22px 20px;
  background: linear-gradient(135deg, #fce7f3 0%, #f3e8ff 100%);
  border: 2px solid #f9a8d4;
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(236, 72, 153, 0.12);
}

.combined__label {
  font-size: 12px;
  color: #a855f7;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.combined__digits {
  font-size: 40px;
  font-weight: 700;
  letter-spacing: 0.1em;
  background: linear-gradient(135deg, #ec4899, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.combined__sparkle {
  position: absolute;
  top: 12px;
  right: 14px;
  color: #ec4899;
  animation: spin 3s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}
</style>