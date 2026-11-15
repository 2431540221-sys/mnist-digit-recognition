<template>
  <div v-if="number" class="combined">
    <div class="combined__header">
      <span class="pulse-dot"></span>
      <span class="combined__label">KẾT QUẢ ĐA CHỮ SỐ (COMBINED)</span>
    </div>
    <strong class="combined__digits">{{ number }}</strong>
  </div>
</template>

<script setup>
import { computed } from 'vue'
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
  gap: 8px;
  padding: 18px 20px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(6, 182, 212, 0.35);
  border-radius: 16px;
  box-shadow:
    0 0 25px rgba(6, 182, 212, 0.15),
    inset 0 0 15px rgba(6, 182, 212, 0.05);
  backdrop-filter: blur(12px);
  margin-bottom: 16px;
}

.combined__header {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #06b6d4;
  box-shadow: 0 0 8px #06b6d4;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

.combined__label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #38bdf8;
  letter-spacing: 0.1em;
  font-weight: 700;
}

.combined__digits {
  font-family: 'JetBrains Mono', monospace;
  font-size: 44px;
  font-weight: 800;
  letter-spacing: 0.15em;
  background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
  line-height: 1;
}
</style>
