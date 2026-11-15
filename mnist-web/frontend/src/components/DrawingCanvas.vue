<template>
  <div class="canvas-wrap">
    <div class="corner corner--tl"></div>
    <div class="corner corner--tr"></div>
    <div class="corner corner--bl"></div>
    <div class="corner corner--br"></div>
    
    <div class="canvas-hud">
      <span class="canvas-hud__label">280×280 RAW CANVAS</span>
      <span class="canvas-hud__coords">NORM: 28×28 COM</span>
    </div>
    
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
  position: relative;
  display: inline-block;
  border-radius: 16px;
  background: #020617;
  padding: 8px;
  border: 1px solid rgba(99, 102, 241, 0.35);
  box-shadow:
    0 0 25px rgba(99, 102, 241, 0.15),
    inset 0 0 15px rgba(0, 0, 0, 0.9);
  transition: all 0.3s ease;
}

.canvas-wrap:hover {
  border-color: rgba(6, 182, 212, 0.6);
  box-shadow:
    0 0 35px rgba(6, 182, 212, 0.25),
    inset 0 0 15px rgba(0, 0, 0, 0.9);
}

/* Futuristic corner accents */
.corner {
  position: absolute;
  width: 10px;
  height: 10px;
  border-color: #06b6d4;
  border-style: solid;
  pointer-events: none;
  z-index: 2;
  transition: border-color 0.2s;
}

.corner--tl { top: -1px; left: -1px; border-width: 2px 0 0 2px; border-top-left-radius: 16px; }
.corner--tr { top: -1px; right: -1px; border-width: 2px 2px 0 0; border-top-right-radius: 16px; }
.corner--bl { bottom: -1px; left: -1px; border-width: 0 0 2px 2px; border-bottom-left-radius: 16px; }
.corner--br { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; border-bottom-right-radius: 16px; }

.canvas-hud {
  position: absolute;
  top: 14px;
  left: 14px;
  right: 14px;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  z-index: 1;
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  color: rgba(148, 163, 184, 0.4);
  letter-spacing: 0.08em;
}

canvas {
  display: block;
  cursor: crosshair;
  touch-action: none;
  border-radius: 10px;
  background: #000000;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.8);
}
</style>
