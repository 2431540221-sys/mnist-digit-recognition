<template>
  <div class="result">
    <div class="result__head">
      <div>
        <div class="result__meta">
          <span class="pulse-indicator" :class="{ 'is-low': result.low_confidence }"></span>
          <span v-if="multi" class="result__tag">VÙNG SỐ #{{ index + 1 }}</span>
          <span v-else class="result__tag">KẾT QUẢ PHÂN LOẠI</span>
        </div>
        <div class="result__number-wrap">
          <span class="result__digit">{{ result.digit }}</span>
        </div>
      </div>

      <div class="result__status">
        <span
          v-if="result.confidence != null"
          class="badge"
          :class="badgeClass"
        >
          <AppIcon :name="badgeIcon" :size="12" />
          <span>{{ (result.confidence * 100).toFixed(1) }}% TIN CẬY</span>
        </span>
      </div>
    </div>

    <!-- Cảnh báo khi confidence thấp, cho phép user chọn số khác -->
    <div
      v-if="result.low_confidence && result.top_3 && result.top_3.length > 1"
      class="alt"
    >
      <div class="alt__header">
        <AppIcon name="alert" :size="13" tone="amber" />
        <span>Độ tin cậy chưa cao — Gợi ý Top 3:</span>
      </div>
      <div class="alt__list">
        <button
          v-for="(alt, altIdx) in result.top_3"
          :key="altIdx"
          type="button"
          :class="{ 'alt__btn': true, 'is-active': alt.digit === result.digit }"
          @click="onSelect(alt.digit)"
          :title="`Xác suất ${(alt.probability * 100).toFixed(1)}%`"
        >
          <span class="alt__digit">{{ alt.digit }}</span>
          <span class="alt__conf">{{ (alt.probability * 100).toFixed(0) }}%</span>
        </button>
      </div>
    </div>

    <!-- Phân phối xác suất 10 chữ số (0-9) -->
    <div class="probs-section">
      <div class="probs-section__title">
        <span>PHÂN PHỐI XÁC SUẤT (SOFTMAX PROBABILITIES)</span>
      </div>

      <div v-if="result.probabilities" class="probs">
        <div v-for="(prob, digit) in result.probabilities" :key="digit" class="probs__row">
          <span class="probs__label" :class="{ 'is-active': Number(digit) === result.digit }">
            {{ digit }}
          </span>
          <div class="probs__track">
            <div
              class="probs__fill"
              :class="{ 'is-top': Number(digit) === result.digit }"
              :style="{ width: Math.max(prob * 100, 1) + '%' }"
            ></div>
          </div>
          <span class="probs__val" :class="{ 'is-active': Number(digit) === result.digit }">
            {{ (prob * 100).toFixed(1) }}%
          </span>
        </div>
      </div>
      <p v-else class="probs__empty">
        Không có dữ liệu phân phối xác suất.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  result: { type: Object, required: true },
  index: { type: Number, required: true },
  multi: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])

function onSelect(digit) {
  if (digit !== props.result.digit) {
    emit('select', { index: props.index, digit })
  }
}

const badgeClass = computed(() => {
  const conf = props.result.confidence || 0
  if (conf >= 0.85) return 'badge--high'
  if (conf >= 0.70) return 'badge--med'
  return 'badge--low'
})

const badgeIcon = computed(() => {
  const conf = props.result.confidence || 0
  if (conf >= 0.85) return 'check'
  if (conf >= 0.70) return 'info'
  return 'alert'
})
</script>

<style scoped>
.result {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 18px 20px;
  backdrop-filter: blur(14px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  margin-bottom: 14px;
  transition: all 0.2s ease;
}

.result:hover {
  border-color: rgba(99, 102, 241, 0.3);
}

.result__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
}

.result__meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.pulse-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.pulse-indicator.is-low {
  background: #f59e0b;
  box-shadow: 0 0 8px #f59e0b;
}

.result__tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #94a3b8;
  letter-spacing: 0.06em;
  font-weight: 600;
}

.result__number-wrap {
  display: flex;
  align-items: baseline;
}

.result__digit {
  font-family: 'JetBrains Mono', monospace;
  font-size: 52px;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, #f8fafc 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 25px rgba(56, 189, 248, 0.4);
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px;
  border-radius: 999px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.badge--high {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.35);
  color: #34d399;
}

.badge--med {
  background: rgba(6, 182, 212, 0.12);
  border: 1px solid rgba(6, 182, 212, 0.35);
  color: #38bdf8;
}

.badge--low {
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #fbbf24;
}

/* Alternatives */
.alt {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 12px;
  padding: 10px 12px;
  margin-bottom: 16px;
}

.alt__header {
  margin: 0 0 8px;
  font-size: 12px;
  color: #fbbf24;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.alt__list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.alt__btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 12px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  min-width: 50px;
  transition: all 0.15s ease;
  color: #cbd5e1;
}

.alt__btn:hover {
  border-color: rgba(6, 182, 212, 0.5);
  background: rgba(30, 41, 59, 0.9);
  transform: translateY(-1px);
}

.alt__btn.is-active {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.9) 0%, rgba(6, 182, 212, 0.9) 100%);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.4);
}

.alt__digit {
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
}

.alt__conf {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  opacity: 0.8;
  margin-top: 3px;
}

/* Probabilities section */
.probs-section {
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.probs-section__title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #64748b;
  letter-spacing: 0.08em;
  margin-bottom: 10px;
  font-weight: 600;
}

.probs {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.probs__row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.probs__label {
  font-family: 'JetBrains Mono', monospace;
  width: 16px;
  text-align: center;
  font-weight: 600;
  color: #64748b;
  font-size: 12px;
}

.probs__label.is-active {
  color: #38bdf8;
  font-weight: 800;
  text-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
}

.probs__track {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 999px;
  overflow: hidden;
}

.probs__fill {
  height: 100%;
  background: #334155;
  border-radius: 999px;
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.probs__fill.is-top {
  background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%);
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.6);
}

.probs__val {
  font-family: 'JetBrains Mono', monospace;
  width: 48px;
  text-align: right;
  color: #64748b;
  font-size: 11px;
  font-variant-numeric: tabular-nums;
}

.probs__val.is-active {
  color: #38bdf8;
  font-weight: 700;
}

.probs__empty {
  color: #64748b;
  font-size: 12px;
  font-style: italic;
  margin: 0;
}
</style>
