<template>
  <div class="result">
    <div class="result__head">
      <div>
        <p class="result__label">
          <AppIcon v-if="multi" name="image" :size="12" />
          <AppIcon v-else name="sparkles" :size="12" />
          <span v-if="multi">Số thứ {{ index + 1 }}</span>
          <span v-else>Mình đoán nè</span>
        </p>
        <p class="result__digit">{{ result.digit }}</p>
      </div>
      <span v-if="result.confidence != null" class="badge">
        <AppIcon name="heart" :size="12" />
        <span>{{ (result.confidence * 100).toFixed(1) }}%</span>
      </span>
    </div>

    <div
      v-if="result.low_confidence && result.top_3 && result.top_3.length > 1"
      class="alt"
    >
      <p class="alt__hint">
        <AppIcon name="help" :size="14" />
        <span>Mình chưa chắc lắm — bạn chọn giúp nha</span>
      </p>
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

    <div v-if="result.probabilities" class="probs">
      <div v-for="(prob, digit) in result.probabilities" :key="digit" class="probs__row">
        <span class="probs__label">{{ digit }}</span>
        <div class="probs__track">
          <div
            class="probs__fill"
            :class="{ 'is-top': Number(digit) === result.digit }"
            :style="{ width: prob * 100 + '%' }"
          ></div>
        </div>
        <span class="probs__val">{{ (prob * 100).toFixed(1) }}%</span>
      </div>
    </div>
    <p v-else class="probs__empty">
      Backend chưa trả về phân phối xác suất.
    </p>
  </div>
</template>

<script setup>
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
</script>

<style scoped>
.result {
  background: #ffffff;
  border: 2px solid #fbcfe8;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.05);
}

.result__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 12px;
}

.result__label {
  margin: 0 0 4px;
  font-size: 12px;
  color: #a855f7;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.result__digit {
  margin: 0;
  font-size: 34px;
  font-weight: 700;
  color: #ec4899;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 2px 8px rgba(236, 72, 153, 0.1);
}

.badge {
  background: linear-gradient(135deg, #fce7f3, #f3e8ff);
  color: #a855f7;
  border: 1.5px solid #f9a8d4;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Alternatives */
.alt {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border: 2px solid #fde68a;
  border-radius: 12px;
  padding: 10px 12px;
  margin-bottom: 12px;
}

.alt__hint {
  margin: 0 0 8px;
  font-size: 12px;
  color: #92400e;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.alt__list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.alt__btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6px 10px;
  background: #ffffff;
  border: 1.5px solid #f3e8ff;
  border-radius: 10px;
  cursor: pointer;
  min-width: 52px;
  transition: all 0.15s;
}

.alt__btn:hover {
  border-color: #f9a8d4;
  transform: translateY(-1px);
}

.alt__btn.is-active {
  background: linear-gradient(135deg, #f9a8d4, #c4b5fd);
  color: #ffffff;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.3);
}

.alt__digit {
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
}

.alt__conf {
  font-size: 10px;
  opacity: 0.75;
  margin-top: 2px;
}

/* Probabilities */
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
  width: 14px;
  text-align: right;
  font-weight: 700;
  color: #6b5b7a;
}

.probs__track {
  flex: 1;
  height: 8px;
  background: #fdf2f8;
  border-radius: 999px;
  overflow: hidden;
}

.probs__fill {
  height: 100%;
  background: #fbcfe8;
  border-radius: 999px;
  transition: width 0.4s ease;
}

.probs__fill.is-top {
  background: linear-gradient(90deg, #f9a8d4, #c4b5fd);
}

.probs__val {
  width: 44px;
  text-align: right;
  color: #8b7a9c;
  font-variant-numeric: tabular-nums;
}

.probs__empty {
  color: #a78bfa;
  font-size: 12px;
  font-style: italic;
  margin: 0;
}
</style>