<template>
  <div v-if="error" class="error-terminal" role="alert">
    <div class="error-terminal__icon">
      <AppIcon name="alert" :size="32" />
    </div>
    <h3 class="error-terminal__title">KHÔNG THỂ NHẬN DIỆN</h3>
    <p class="error-terminal__msg">{{ error }}</p>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import { usePredict } from '../composables/usePredict.js'

const { error } = usePredict()
</script>

<style scoped>
.error-terminal {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px 40px;
  border: 1px dashed rgba(239, 68, 68, 0.45);
  border-radius: 18px;
  background: rgba(239, 68, 68, 0.06);
  color: #b91c1c;
}

.error-terminal__icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.1);
  margin-bottom: 18px;
}

.error-terminal__title {
  margin: 0 0 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #991b1b;
}

.error-terminal__msg {
  margin: 0;
  max-width: 380px;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.6;
}
</style>
