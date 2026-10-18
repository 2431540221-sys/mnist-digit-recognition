<template>
  <div class="actions">
    <button class="btn btn--ghost" type="button" @click="onClear">
      <AppIcon name="trash" :size="16" />
      <span>Xóa hết</span>
    </button>
    <button
      class="btn btn--primary"
      type="button"
      :disabled="loading"
      @click="onPredict"
    >
      <span v-if="loading" class="spinner" aria-hidden="true"></span>
      <AppIcon v-else name="sparkles" :size="16" />
      <span>{{ loading ? 'Đang đoán…' : 'Dự đoán' }}</span>
    </button>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import { useAppState } from '../composables/useAppState.js'
import { usePredict } from '../composables/usePredict.js'
import { useHistory } from '../composables/useHistory.js'

const { clearAll, uploadedImageDataUrl, currentMode, toDataURL } = useAppState()
const { predict, loading } = usePredict()
const { add: addHistory } = useHistory()

function onClear() {
  clearAll()
}

async function onPredict() {
  const dataUrl =
    uploadedImageDataUrl.value ||
    (toDataURL ? toDataURL(document.querySelector('canvas')) : null)
  if (!dataUrl) return
  try {
    await predict(dataUrl, currentMode.value)
    const now = new Date()
    const timeStr = now.toLocaleString('vi-VN')
    const { results } = usePredict()
    addHistory({
      time: timeStr,
      mode: currentMode.value,
      digits: (results.value || []).map((r) => r.digit),
    })
  } catch {
    // usePredict đã set error
  }
}
</script>

<style scoped>
.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
}

.btn {
  flex: 1;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 700;
  border-radius: 14px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn:focus-visible {
  outline: 2px solid #ec4899;
  outline-offset: 2px;
}

.btn--ghost {
  background: #ffffff;
  border-color: #fbcfe8;
  color: #a855f7;
}

.btn--ghost:hover {
  background: #fdf2f8;
  border-color: #f9a8d4;
  transform: translateY(-1px);
}

.btn--primary {
  background: linear-gradient(135deg, #f9a8d4, #c4b5fd);
  color: #ffffff;
  border-color: transparent;
  flex: 2;
  box-shadow: 0 4px 14px rgba(236, 72, 153, 0.3);
}

.btn--primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4);
}

.btn--primary:disabled {
  background: #d8b4d8;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}
</style>