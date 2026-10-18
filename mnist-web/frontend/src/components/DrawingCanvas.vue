<template>
  <div class="canvas-wrap">
    <canvas ref="canvasRef" width="280" height="280" aria-label="Khung vẽ chữ số"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppState } from '../composables/useAppState.js'

const { setCanvasRef } = useAppState()
const canvasRef = ref(null)

onMounted(() => {
  setCanvasRef(canvasRef.value)
})
</script>

<style scoped>
.canvas-wrap {
  display: inline-block;
  border: 3px solid #f9a8d4;
  border-radius: 18px;
  background: #ffffff;
  padding: 6px;
  box-shadow:
    inset 0 2px 6px rgba(236, 72, 153, 0.08),
    0 4px 16px rgba(236, 72, 153, 0.1);
}

canvas {
  display: block;
  cursor: crosshair;
  touch-action: none;
  border-radius: 12px;
}
</style>