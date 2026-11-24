<template>
  <div class="page">
    <!-- Ambient Tech Glow Background -->
    <div class="ambient-glow" aria-hidden="true">
      <div class="glow-orb glow-orb--1"></div>
      <div class="glow-orb glow-orb--2"></div>
      <div class="grid-overlay"></div>
    </div>

    <div class="app-shell">
      <!-- Top Header / Telemetry Bar -->
      <header class="top-nav">
        <div class="brand">
          <div class="brand__icon">
            <AppIcon name="cpu" :size="20" tone="cyan" />
          </div>
          <div>
            <h1 class="brand__title">MNIST NEURAL LAB</h1>
            <p class="brand__subtitle">Hệ thống Nhận diện Chữ số Viết tay · Computer Vision</p>
          </div>
        </div>

        <div class="telemetry">
          <div class="telemetry__item">
            <span class="telemetry__dot"></span>
            <span class="telemetry__label">STATUS:</span>
            <span class="telemetry__val telemetry__val--green">READY</span>
          </div>
          <div class="telemetry__item telemetry__item--hide-mobile">
            <span class="telemetry__label">MODEL:</span>
            <span class="telemetry__val">CNN 4 Conv2D</span>
          </div>
          <div class="telemetry__item telemetry__item--hide-mobile">
            <span class="telemetry__label">ACCURACY:</span>
            <span class="telemetry__val telemetry__val--cyan">99.47%</span>
          </div>
        </div>
      </header>

      <!-- Main Studio Dashboard -->
      <main class="dashboard">
        <!-- LEFT COLUMN: Input Workspace -->
        <section class="card card--studio">
          <div class="card__head">
            <div class="card__head-title">
              <AppIcon name="layers" :size="16" tone="cyan" />
              <span>KHÔNG GIAN NHẬP LIỆU</span>
            </div>
          </div>

          <ModeTabs />

          <div class="seg" role="tablist" aria-label="Chọn phương thức vẽ">
            <button
              role="tab"
              :aria-selected="inputTab === 'draw'"
              :class="{ seg__btn: true, 'is-active': inputTab === 'draw' }"
              @click="setInputTab('draw')"
            >
              <AppIcon name="pencil-line" :size="14" />
              <span>Vẽ tay</span>
            </button>
            <button
              role="tab"
              :aria-selected="inputTab === 'upload'"
              :class="{ seg__btn: true, 'is-active': inputTab === 'upload' }"
              @click="setInputTab('upload')"
            >
              <AppIcon name="upload" :size="14" />
              <span>Tải ảnh</span>
            </button>
            <button
              role="tab"
              :aria-selected="inputTab === 'camera'"
              :class="{ seg__btn: true, 'is-active': inputTab === 'camera' }"
              @click="setInputTab('camera')"
            >
              <AppIcon name="camera" :size="14" />
              <span>Webcam</span>
            </button>
          </div>

          <div class="stage">
            <DrawingCanvas v-if="inputTab === 'draw'" />
            <ImageDropZone v-else-if="inputTab === 'upload'" @fileSelected="onUploadFile" />
            <CameraCapture v-else-if="inputTab === 'camera'" @captured="onCameraCapture" @retake="onCameraRetake" />
          </div>

          <BrushToolbar v-if="inputTab === 'draw'" />

          <ActionButtons />

          <TipsBox />
        </section>

        <!-- RIGHT COLUMN: Neural Inference & Diagnostics -->
        <section class="card card--inference">
          <div class="card__head">
            <div class="card__head-title">
              <AppIcon name="activity" :size="16" tone="indigo" />
              <span>KẾT QUẢ SUY LUẬN AI</span>
            </div>
            <span class="card__badge">INFERENCE ENGINE</span>
          </div>

          <!-- Khi có lỗi: hiện ngay tại khung chờ tín hiệu đầu vào -->
          <ErrorBanner v-if="error" />

          <!-- Khi đã có kết quả dự đoán -->
          <div v-else-if="results && results.length" class="results-stream">
            <CombinedResult />
            <ResultCard
              v-for="(result, index) in results"
              :key="index"
              :result="result"
              :index="index"
              :multi="currentMode === 'multi'"
              @select="onSelectAlternative"
            />
          </div>

          <!-- Khi chưa dự đoán (Trạng thái chờ) -->
          <div v-else class="idle-terminal">
            <div class="radar-box">
              <div class="radar-ring radar-ring--1"></div>
              <div class="radar-ring radar-ring--2"></div>
              <div class="radar-sweep"></div>
              <AppIcon name="brain" :size="32" tone="cyan" class="radar-center-icon" />
            </div>

            <h3 class="idle-title">ĐANG CHỜ TÍN HIỆU ĐẦU VÀO</h3>
            <p class="idle-desc">
              Vẽ một hoặc nhiều chữ số vào bảng vẽ bên trái rồi nhấn <strong>"Nhận diện ngay"</strong> để kích hoạt mạng nơ-ron tích chập (CNN).
            </p>

            <div class="pipeline-spec">
              <div class="pipeline-spec__head">
                <AppIcon name="terminal" :size="12" tone="cyan" />
                <span>PIPELINE XỬ LÝ ẢNH & KIẾN TRÚC MẠNG</span>
              </div>
              <div class="pipeline-spec__steps">
                <div class="pipeline-step">
                  <span class="pipeline-step__num">01</span>
                  <span>Gaussian Blur + Otsu Thresholding</span>
                </div>
                <div class="pipeline-step">
                  <span class="pipeline-step__num">02</span>
                  <span>Contour Segment + Aspect-Ratio 20×20</span>
                </div>
                <div class="pipeline-step">
                  <span class="pipeline-step__num">03</span>
                  <span class="pipeline-step__highlight">Center of Mass (COM) Alignment</span>
                </div>
                <div class="pipeline-step">
                  <span class="pipeline-step__num">04</span>
                  <span>CNN 4-Conv2D + BatchNorm + Softmax</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Lịch sử dự đoán -->
          <HistoryList />
        </section>
      </main>

      <!-- Thông tin dữ liệu & kiến trúc CNN (lấy từ backend) -->
      <ModelInfoPanel />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppIcon from './components/AppIcon.vue'
import ModeTabs from './components/ModeTabs.vue'
import DrawingCanvas from './components/DrawingCanvas.vue'
import ImageDropZone from './components/ImageDropZone.vue'
import CameraCapture from './components/CameraCapture.vue'
import BrushToolbar from './components/BrushToolbar.vue'
import ActionButtons from './components/ActionButtons.vue'
import TipsBox from './components/TipsBox.vue'
import ResultCard from './components/ResultCard.vue'
import CombinedResult from './components/CombinedResult.vue'
import ErrorBanner from './components/ErrorBanner.vue'
import HistoryList from './components/HistoryList.vue'
import ModelInfoPanel from './components/ModelInfoPanel.vue'

import { useAppState } from './composables/useAppState.js'
import { usePredict } from './composables/usePredict.js'

const { currentMode, setUploadedImage } = useAppState()
const { results, error, overrideDigit } = usePredict()

const inputTab = ref('draw')

function setInputTab(tab) {
  inputTab.value = tab
  setUploadedImage(null)
}

function onUploadFile(dataUrl) {
  setUploadedImage(dataUrl)
}

function onCameraCapture(dataUrl) {
  setUploadedImage(dataUrl)
}

function onCameraRetake() {
  setUploadedImage(null)
}

function onSelectAlternative({ index, digit }) {
  overrideDigit(index, digit)
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

*,
*::before,
*::after {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  font-size: 14px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  color: #334155;
  background: #f4f7fb;
  overflow-x: hidden;
}

button {
  font-family: inherit;
}
</style>

<style scoped>
.page {
  position: relative;
  min-height: 100vh;
  padding: 24px 16px 40px;
  display: flex;
  justify-content: center;
  background-color: #f4f7fb;
}

/* Ambient glow & grid */
.ambient-glow {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.14;
}

.glow-orb--1 {
  top: -10%;
  left: 15%;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #4f46e5 0%, transparent 70%);
}

.glow-orb--2 {
  bottom: 0%;
  right: 15%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #06b6d4 0%, transparent 70%);
}

.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(to right, rgba(15, 23, 42, 0.035) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(15, 23, 42, 0.035) 1px, transparent 1px);
  background-size: 40px 40px;
}

.app-shell {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1080px;
}

/* Top Nav */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 18px;
  backdrop-filter: blur(16px);
  margin-bottom: 20px;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.10);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand__icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
}

.brand__title {
  margin: 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 16px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: 0.06em;
}

.brand__subtitle {
  margin: 0;
  font-size: 11px;
  color: #64748b;
}

.telemetry {
  display: flex;
  align-items: center;
  gap: 14px;
}

.telemetry__item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(241, 245, 249, 0.9);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
}

.telemetry__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.telemetry__label {
  color: #64748b;
  font-weight: 600;
}

.telemetry__val {
  color: #334155;
  font-weight: 700;
}

.telemetry__val--green {
  color: #059669;
}

.telemetry__val--cyan {
  color: #0369a1;
}

/* Dashboard 2-column layout */
.dashboard {
  display: grid;
  grid-template-columns: 440px 1fr;
  gap: 20px;
  align-items: start;
}

@media (max-width: 920px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
  .telemetry__item--hide-mobile {
    display: none;
  }
}

/* Cards */
.card {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 22px;
  padding: 22px;
  backdrop-filter: blur(16px);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.10);
}

.card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.card__head-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: 0.06em;
}

.card__badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #4f46e5;
  letter-spacing: 0.06em;
}

/* Segmented tab */
.seg {
  display: flex;
  background: rgba(241, 245, 249, 0.9);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 16px;
  gap: 4px;
}

.seg__btn {
  flex: 1;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.15s ease;
}

.seg__btn:hover:not(.is-active) {
  color: #334155;
  background: rgba(15, 23, 42, 0.04);
}

.seg__btn.is-active {
  background: #ffffff;
  color: #0369a1;
  border: 1px solid rgba(6, 182, 212, 0.35);
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.10);
}

.stage {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 4px 0 10px;
}

/* Idle State in Right Column */
.idle-terminal {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 36px 20px 24px;
  border: 1px dashed rgba(15, 23, 42, 0.08);
  border-radius: 18px;
  background: rgba(241, 245, 249, 0.9);
}

.radar-box {
  position: relative;
  width: 90px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.radar-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(6, 182, 212, 0.25);
}

.radar-ring--1 { width: 50px; height: 50px; }
.radar-ring--2 { width: 90px; height: 90px; border-color: rgba(99, 102, 241, 0.2); }

.radar-sweep {
  position: absolute;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, transparent 0deg, rgba(6, 182, 212, 0.25) 60deg, transparent 65deg);
  animation: radar 3s linear infinite;
}

@keyframes radar {
  100% { transform: rotate(360deg); }
}

.radar-center-icon {
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 0 10px rgba(6, 182, 212, 0.6));
}

.idle-title {
  margin: 0 0 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: 0.08em;
}

.idle-desc {
  margin: 0 0 24px;
  font-size: 12px;
  color: #64748b;
  max-width: 380px;
  line-height: 1.6;
}

.idle-desc strong {
  color: #0369a1;
}

/* Pipeline Spec Box */
.pipeline-spec {
  width: 100%;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 12px;
  padding: 12px 16px;
  text-align: left;
}

.pipeline-spec__head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  color: #0369a1;
  letter-spacing: 0.06em;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.pipeline-spec__steps {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pipeline-step {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #94a3b8;
}

.pipeline-step__num {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 700;
}

.pipeline-step__highlight {
  color: #059669;
  font-weight: 600;
}
</style>
