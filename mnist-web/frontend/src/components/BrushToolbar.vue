<template>
  <div class="bar">
    <button
      class="chip"
      :disabled="!canUndo"
      title="Hoàn tác (Ctrl+Z)"
      @click="undo"
    >
      <AppIcon name="undo" :size="16" />
    </button>
    <button
      class="chip"
      :disabled="!canRedo"
      title="Làm lại (Ctrl+Y)"
      @click="redo"
    >
      <AppIcon name="redo" :size="16" />
    </button>

    <div class="bar__divider"></div>

    <label class="size">
      <span class="size__label">
        <AppIcon name="pencil" :size="14" tone="purple" />
        <span>Cỡ nét</span>
      </span>
      <input
        type="range"
        min="4"
        max="40"
        step="2"
        :value="brushSize"
        @input="onSizeChange"
        class="size__slider"
      />
      <span class="size__val">{{ brushSize }}px</span>
    </label>

    <div class="bar__divider"></div>

    <button class="chip chip--text" @click="clear" type="button">
      <AppIcon name="eraser" :size="14" />
      <span>Xóa</span>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import AppIcon from './AppIcon.vue'
import { useCanvas } from '../composables/useCanvas.js'

const {
  undo: doUndo,
  redo: doRedo,
  clear: doClear,
  canUndo,
  canRedo,
  setBrushSize,
} = useCanvas()

const brushSize = ref(15)

function onSizeChange(e) {
  const v = Number(e.target.value)
  brushSize.value = v
  setBrushSize(v)
}

function undo() { doUndo() }
function redo() { doRedo() }
function clear() { doClear() }

function onKey(e) {
  const mod = e.ctrlKey || e.metaKey
  if (!mod) return
  const key = e.key.toLowerCase()
  if (key === 'z') {
    e.preventDefault()
    e.shiftKey ? doRedo() : doUndo()
  } else if (key === 'y') {
    e.preventDefault()
    doRedo()
  }
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding: 10px 12px;
  background: #ffffff;
  border: 2px solid #fbcfe8;
  border-radius: 16px;
  flex-wrap: wrap;
}

.chip {
  min-width: 38px;
  height: 36px;
  padding: 0 10px;
  background: #fdf2f8;
  border: 1.5px solid #fbcfe8;
  border-radius: 10px;
  color: #ec4899;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.15s;
}

.chip:hover:not(:disabled) {
  background: #fce7f3;
  border-color: #f9a8d4;
  transform: translateY(-1px);
}

.chip:disabled {
  color: #d8b4d8;
  border-color: #f3e8ff;
  cursor: not-allowed;
  background: #faf5ff;
}

.chip--text {
  font-size: 12px;
  padding: 0 12px;
}

.bar__divider {
  width: 1px;
  height: 24px;
  background: #fbcfe8;
}

.size {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 180px;
}

.size__label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #8b7a9c;
  font-weight: 600;
}

.size__slider {
  flex: 1;
  max-width: 120px;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: #fbcfe8;
  border-radius: 999px;
  outline: none;
  cursor: pointer;
}

.size__slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f9a8d4, #c4b5fd);
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1.5px #ec4899;
  cursor: pointer;
}

.size__slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f9a8d4, #c4b5fd);
  border: 2px solid #ffffff;
  cursor: pointer;
}

.size__val {
  font-size: 12px;
  color: #ec4899;
  font-weight: 700;
  min-width: 40px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

@media (max-width: 420px) {
  .bar {
    gap: 6px;
  }
  .size {
    min-width: 140px;
  }
  .size__label span {
    display: none;
  }
}
</style>