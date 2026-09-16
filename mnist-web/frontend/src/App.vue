<template>
  <div class="app-background">
    <div class="container glass-panel">
      <h1>Nhận diện chữ số viết tay</h1>

      <div class="tabs">
        <button :class="['tab-btn', { active: currentMode === 'single' }]" @click="setMode('single')">Đoán 1 số</button>
        <button :class="['tab-btn', { active: currentMode === 'multi' }]" @click="setMode('multi')">Đoán nhiều số</button>
      </div>
      <p class="subtitle">{{ currentMode === 'single' ? 'Vẽ hoặc tải ảnh 1 chữ số lên' : 'Vẽ hoặc tải ảnh nhiều chữ số — model cắt và đoán từng số' }}</p>

      <!-- KHU VỰC NHẬP DUY NHẤT -->
      <div class="input-area">
        <!-- Canvas luôn ở trong DOM (v-show giữ context), ẩn khi có ảnh upload -->
        <div class="canvas-wrapper" v-show="!uploadedImageDataUrl">
          <canvas
            ref="canvasRef"
            width="280"
            height="280"
            @mousedown="startDrawing"
            @mousemove="draw"
            @mouseup="stopDrawing"
            @mouseleave="stopDrawing"
            @touchstart.prevent="handleTouchStart"
            @touchmove.prevent="handleTouchMove"
            @touchend.prevent="stopDrawing"
          ></canvas>
        </div>
        <!-- Preview ảnh upload -->
        <div v-if="uploadedImageDataUrl" class="image-preview-box">
          <img :src="uploadedImageDataUrl" class="upload-preview" />
        </div>
      </div>

      <input ref="fileInputRef" type="file" accept="image/*" style="display:none" @change="handleFileUpload" />

      <div class="buttons">
        <button class="btn btn-clear" @click="uploadedImageDataUrl ? clearUpload() : clearCanvas()">Xóa</button>
        <button class="btn btn-upload" @click="triggerUpload">Tải ảnh lên</button>
        <button class="btn btn-predict" @click="predict" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? 'Đang đoán...' : 'Dự đoán' }}
        </button>
      </div>

      <!-- LƯU Ý -->
      <div class="tips-box">
        <div class="tips-header">📝 <strong>Lưu ý để model đoán chính xác hơn:</strong></div>
        <ul class="tips-list">
          <li>Viết cách nhau rõ ràng, đừng để 2 số dính/chạm vào nhau</li>
          <li>Viết nét đậm, đơn giản, tránh bay bướm hay thêm nét thừa</li>
          <li>Viết chữ số đủ to, chiếm phần lớn chiều cao khung vẽ</li>
          <li>Canh chữ số nằm giữa dòng, không quá sát mép trên/dưới</li>
        </ul>
      </div>

      <!-- KẾT QUẢ -->
      <div v-if="results && results.length" class="results-container">
        <div v-for="(result, index) in results" :key="index" class="result">
          <p class="predicted">
            <span v-if="currentMode === 'multi'">Số thứ {{ index + 1 }}: </span>
            <span v-else>Model đoán: </span>
            <strong class="glow-text">{{ result.digit }}</strong>
          </p>
          <div class="probabilities">
            <div v-for="(prob, digit) in result.probabilities" :key="digit" class="prob-row">
              <span class="digit-label">{{ digit }}</span>
              <div class="prob-bar-bg">
                <div class="prob-bar-fill" :style="{ width: (prob * 100) + '%' }" :class="{ highlight: Number(digit) === result.digit }"></div>
              </div>
              <span class="prob-value">{{ (prob * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div v-if="history.length" class="history-section">
        <div class="history-header">
          <span class="history-title">📋 Lịch sử dự đoán ({{ history.length }})</span>
          <button class="btn btn-download" @click="downloadHistory">⬇ Tải xuống</button>
        </div>
        <div class="history-list">
          <div v-for="(entry, i) in history" :key="i" class="history-item">
            <span class="history-time">{{ entry.time }}</span>
            <span class="history-mode">[{{ entry.mode === 'single' ? '1 số' : 'Nhiều số' }}]</span>
            <span class="history-digits">→ <strong>{{ entry.digits.join(', ') }}</strong></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const canvasRef = ref(null)
const fileInputRef = ref(null)
let ctx = null
let drawing = false

const results = ref(null)
const error = ref('')
const loading = ref(false)
const currentMode = ref('single')
const history = ref([])
const uploadedImageDataUrl = ref(null) // Lưu ảnh gốc khi user upload (không qua canvas)

function setMode(mode) {
  currentMode.value = mode
  clearCanvas()
}

// Sửa lại URL này nếu backend chạy ở địa chỉ/port khác
const API_URL = 'http://localhost:5000/predict'

onMounted(() => {
  ctx = canvasRef.value.getContext('2d')
  resetCanvasStyle()
})

function resetCanvasStyle() {
  ctx.fillStyle = 'black'
  ctx.fillRect(0, 0, 280, 280)
  ctx.strokeStyle = 'white'
  ctx.lineWidth = 15
  ctx.lineCap = 'round'
}

function getPos(e) {
  const rect = canvasRef.value.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

function startDrawing(e) {
  drawing = true
  const { x, y } = getPos(e)
  ctx.strokeStyle = 'white'
  ctx.lineWidth = 15
  ctx.lineCap = 'round'
  ctx.beginPath()
  ctx.moveTo(x, y)
}
function draw(e) {
  if (!drawing) return
  const { x, y } = getPos(e)
  ctx.lineTo(x, y)
  ctx.stroke()
}
function stopDrawing() {
  drawing = false
}

function handleTouchStart(e) {
  const touch = e.touches[0]
  startDrawing(touch)
}
function handleTouchMove(e) {
  const touch = e.touches[0]
  draw(touch)
}

function clearCanvas() {
  resetCanvasStyle()
  results.value = null
  error.value = ''
  uploadedImageDataUrl.value = null
}

async function predict() {
  error.value = ''
  loading.value = true
  try {
    // Ưu tiên ảnh upload nếu có, không thì đọc canvas
    const dataUrl = uploadedImageDataUrl.value || canvasRef.value.toDataURL('image/png')
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: dataUrl, mode: currentMode.value })
    })
    if (!res.ok) {
      const errData = await res.json()
      throw new Error(errData.error || 'Lỗi từ server')
    }
    const data = await res.json()
    results.value = data.results
    // Push to history
    const now = new Date()
    const timeStr = now.toLocaleString('vi-VN')
    history.value.unshift({
      time: timeStr,
      mode: currentMode.value,
      digits: data.results.map(r => r.digit)
    })
  } catch (err) {
    error.value = err.message.includes('fetch')
      ? 'Không kết nối được backend. Kiểm tra đã chạy "python app.py" chưa.'
      : err.message
  } finally {
    loading.value = false
  }
}

function triggerUpload() {
  fileInputRef.value.click()
}

function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  _loadFile(file)
  event.target.value = ''
}

function handleDrop(event) {
  const file = event.dataTransfer.files[0]
  if (!file) return
  _loadFile(file)
}

function _loadFile(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImageDataUrl.value = e.target.result
    results.value = null
    error.value = ''
  }
  reader.readAsDataURL(file)
}

function clearUpload() {
  uploadedImageDataUrl.value = null
  results.value = null
  error.value = ''
  resetCanvasStyle()
}

function downloadHistory() {
  if (!history.value.length) return
  const lines = history.value.map(entry => {
    const mode = entry.mode === 'single' ? '1 số' : 'Nhiều số'
    return `[${entry.time}] Chế độ: ${mode} | Kết quả: ${entry.digits.join(', ')}`
  })
  const content = 'Lịch sử Dự Đoán Chữ Số Viết Tay\n' + '='.repeat(50) + '\n' + lines.join('\n')
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'lich_su_du_doan.txt'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

body, html {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100vh;
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background-color: #0f172a;
}
</style>

<style scoped>
.app-background {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: 
    radial-gradient(circle at 15% 50%, rgba(79, 70, 229, 0.2), transparent 40%),
    radial-gradient(circle at 85% 30%, rgba(236, 72, 153, 0.2), transparent 40%),
    #0f172a;
  animation: pulse-bg 10s ease-in-out infinite alternate;
}

@keyframes pulse-bg {
  0% { background-position: 0% 0%; }
  100% { background-position: 100% 100%; }
}

.container.glass-panel {
  width: 100%;
  max-width: 440px;
  margin: 20px;
  text-align: center;
  padding: 40px 30px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 24px;
  color: #fff;
  z-index: 10;
}

h1 {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #a5b4fc, #fbcfe8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin-bottom: 20px;
  font-weight: 300;
}

.tabs {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px;
  border-radius: 12px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background: linear-gradient(135deg, #4f46e5, #ec4899);
  color: white;
  box-shadow: 0 2px 10px rgba(79, 70, 229, 0.3);
}

.tab-btn:not(.active):hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.canvas-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 24px;
}

.canvas-wrapper::before {
  content: '';
  position: absolute;
  top: -2px; left: -2px; right: -2px; bottom: -2px;
  background: linear-gradient(45deg, #4f46e5, #ec4899);
  z-index: -1;
  border-radius: 14px;
  opacity: 0.5;
  filter: blur(8px);
  transition: opacity 0.3s;
}

.canvas-wrapper:hover::before {
  opacity: 0.8;
}

canvas {
  background-color: #000;
  border-radius: 12px;
  box-shadow: inset 0 0 20px rgba(255,255,255,0.05);
  cursor: crosshair;
  touch-action: none;
  display: block;
}

/* Single input area */
.input-area {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.image-preview-box {
  width: 280px;
  height: 280px;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 0 2px rgba(165, 180, 252, 0.3);
}

.upload-zone:hover {
  border-color: rgba(165, 180, 252, 0.6);
  background: rgba(79, 70, 229, 0.08);
}

.upload-placeholder {
  text-align: center;
  color: #64748b;
}

.upload-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.upload-placeholder p {
  color: #94a3b8;
  font-size: 14px;
  margin: 0 0 4px;
}

.upload-placeholder span {
  font-size: 11px;
  color: #475569;
}

.upload-preview {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 14px;
}

.buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

/* Tips box */
.tips-box {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 16px 20px;
  margin: 0 auto 24px;
  max-width: 480px;
  text-align: left;
  backdrop-filter: blur(10px);
}

.tips-header {
  font-size: 14px;
  color: #fbbf24;
  margin-bottom: 8px;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.6;
}

.tips-list li {
  margin-bottom: 4px;
}

.tips-list li:last-child {
  margin-bottom: 0;
}

.btn {
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: inherit;
}

.btn:active {
  transform: scale(0.96);
}

.btn-clear {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.btn-clear:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-upload {
  background: linear-gradient(135deg, #ec4899, #4f46e5);
  color: white;
  box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);
  border: none;
}

.btn-upload:hover {
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
  transform: translateY(-2px);
}

.btn-predict {
  background: linear-gradient(135deg, #4f46e5, #ec4899);
  color: white;
  box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
}

.btn-predict:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(236, 72, 153, 0.5);
  transform: translateY(-2px);
}

.btn-predict:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(0.4);
  transform: none;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { 100% { transform: rotate(360deg); } }

.results-container {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result {
  background: rgba(0, 0, 0, 0.2);
  padding: 20px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.05);
  animation: fadeUp 0.5s ease-out forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.predicted {
  font-size: 16px;
  color: #cad5e2;
  margin-bottom: 20px;
}

.glow-text {
  font-size: 32px;
  color: #fff;
  text-shadow: 0 0 10px rgba(255,255,255,0.5), 0 0 20px #a5b4fc;
  vertical-align: middle;
  margin-left: 8px;
}

.probabilities {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.prob-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #cbd5e1;
}

.digit-label {
  width: 18px;
  font-weight: 700;
  text-align: right;
  color: #f1f5f9;
}

.prob-bar-bg {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  height: 12px;
  overflow: hidden;
  position: relative;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
}

.prob-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 8px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.prob-bar-fill.highlight {
  background: linear-gradient(90deg, #ec4899, #f43f5e);
  box-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
}

.prob-value {
  width: 48px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: #94a3b8;
}

.error {
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
  padding: 12px;
  border-radius: 8px;
  margin-top: 20px;
  border: 1px solid rgba(248, 113, 113, 0.2);
  font-size: 14px;
}

.history-section {
  margin-top: 30px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
  animation: fadeUp 0.5s ease-out forwards;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.history-title {
  font-size: 14px;
  font-weight: 600;
  color: #94a3b8;
}

.btn-download {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 7px 14px;
  font-size: 13px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.btn-download:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.5);
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px 0;
}

.history-list::-webkit-scrollbar {
  width: 4px;
}
.history-list::-webkit-scrollbar-track {
  background: transparent;
}
.history-list::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.15);
  border-radius: 4px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  transition: background 0.2s;
}

.history-item:last-child {
  border-bottom: none;
}

.history-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.history-time {
  color: #64748b;
  font-size: 11px;
  min-width: 90px;
}

.history-mode {
  color: #7c3aed;
  font-size: 11px;
  font-weight: 600;
  background: rgba(124, 58, 237, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
}

.history-digits {
  color: #e2e8f0;
  font-size: 13px;
}

.history-digits strong {
  color: #a5b4fc;
  font-size: 15px;
}
</style>
