<template>
  <div class="actions">
    <button class="btn btn--ghost" type="button" @click="onClear">
      <AppIcon name="trash" :size="15" />
      <span>Xóa hết</span>
    </button>
    <button
      class="btn btn--primary"
      type="button"
      :disabled="loading"
      @click="onPredict"
    >
      <span v-if="loading" class="spinner" aria-hidden="true"></span>
      <AppIcon v-else name="sparkles" :size="15" />
      <span>{{ loading ? 'Đang phân tích…' : 'Nhận diện ngay' }}</span>
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
    const timeStr = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
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
  margin-top: 14px;
  margin-bottom: 16px;
}

.btn {
  flex: 1;
  padding: 12px 18px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 12px;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: 0.02em;
}

.btn:focus-visible {
  outline: 2px solid #06b6d4;
  outline-offset: 2px;
}

.btn--ghost {
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(15, 23, 42, 0.08);
  color: #94a3b8;
  backdrop-filter: blur(10px);
}

.btn--ghost:hover {
  background: #e2e8f0;
  border-color: rgba(15, 23, 42, 0.16);
  color: #0f172a;
  transform: translateY(-1px);
}

.btn--primary {
  background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
  color: #ffffff;
  flex: 2;
  border-color: transparent;
  box-shadow: 0 4px 18px rgba(79, 70, 229, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn--primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(6, 182, 212, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn--primary:disabled {
  background: #e2e8f0;
  color: #64748b;
  border-color: transparent;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(15, 23, 42, 0.16);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}
</style>
