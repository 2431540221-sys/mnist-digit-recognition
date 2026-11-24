<template>
  <div class="bar">
    <div class="btn-group">
      <button
        class="chip"
        :disabled="!canUndo"
        title="Hoàn tác (Ctrl+Z)"
        @click="undo"
        type="button"
      >
        <AppIcon name="undo" :size="15" />
      </button>
      <button
        class="chip"
        :disabled="!canRedo"
        title="Làm lại (Ctrl+Y)"
        @click="redo"
        type="button"
      >
        <AppIcon name="redo" :size="15" />
      </button>
    </div>

    <div class="bar__divider"></div>

    <label class="size">
      <span class="size__label">
        <AppIcon name="pencil" :size="13" tone="cyan" />
        <span>Nét vẽ</span>
      </span>
      <input
        type="range"
        min="4"
        max="36"
        step="2"
        :value="brushSize"
        @input="onSizeChange"
        class="size__slider"
      />
      <span class="size__val">{{ brushSize }}px</span>
    </label>

    <div class="bar__divider"></div>

    <button class="chip chip--text" @click="clear" type="button" title="Xóa canvas">
      <AppIcon name="eraser" :size="14" tone="soft" />
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
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  backdrop-filter: blur(12px);
  flex-wrap: wrap;
}

.btn-group {
  display: flex;
  gap: 4px;
}

.chip {
  min-width: 34px;
  height: 32px;
  padding: 0 8px;
  background: #f1f5f9;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 8px;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.15s ease;
}

.chip:hover:not(:disabled) {
  background: #e2e8f0;
  border-color: rgba(6, 182, 212, 0.4);
  color: #0369a1;
  transform: translateY(-1px);
}

.chip:disabled {
  color: #94a3b8;
  border-color: transparent;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.92);
}

.chip--text {
  font-size: 12px;
  padding: 0 10px;
}

.bar__divider {
  width: 1px;
  height: 20px;
  background: rgba(15, 23, 42, 0.04);
}

.size {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 170px;
}

.size__label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.size__slider {
  flex: 1;
  max-width: 110px;
  height: 4px;
  -webkit-appearance: none;
  appearance: none;
  background: #e2e8f0;
  border-radius: 999px;
  outline: none;
  cursor: pointer;
}

.size__slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #06b6d4;
  border: 2px solid #ffffff;
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.8);
  cursor: pointer;
  transition: transform 0.15s;
}

.size__slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.size__slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #06b6d4;
  border: 2px solid #ffffff;
  cursor: pointer;
}

.size__val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #0369a1;
  font-weight: 600;
  min-width: 36px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

@media (max-width: 420px) {
  .bar {
    gap: 6px;
  }
  .size {
    min-width: 130px;
  }
  .size__label span {
    display: none;
  }
}
</style>
