<template>
  <div class="camera-wrap">
    <!-- 1. Video Element LUÔN LUÔN được mount trong DOM để videoRef không bao giờ bị null -->
    <video
      ref="videoRef"
      autoplay
      playsinline
      muted
      class="video-feed"
      :class="{ 'is-hidden': Boolean(snapshotUrl) }"
      @loadeddata="onVideoLoaded"
    ></video>

    <!-- Khung ngắm mục tiêu (Target Reticle) khi đang live video -->
    <div v-show="!snapshotUrl && !cameraError && !isLoading" class="viewfinder">
      <div class="reticle-corner reticle-corner--tl"></div>
      <div class="reticle-corner reticle-corner--tr"></div>
      <div class="reticle-corner reticle-corner--bl"></div>
      <div class="reticle-corner reticle-corner--br"></div>
      <div class="reticle-center"></div>
      <span class="reticle-hint">CĂN CHỮ SỐ VÀO GIỮA KHUNG</span>
    </div>

    <!-- Controls khi đang mở cam (Chụp / Đổi cam) -->
    <div v-show="!snapshotUrl && !cameraError && !isLoading" class="camera-controls">
      <button
        v-if="hasMultipleCameras"
        class="ctrl-btn ctrl-btn--flip"
        type="button"
        title="Đổi camera trước/sau"
        @click="flipCamera"
      >
        <AppIcon name="rotate" :size="14" />
      </button>

      <button
        class="capture-btn"
        type="button"
        title="Chụp ảnh chữ số"
        @click="takeSnapshot"
      >
        <div class="capture-btn__inner"></div>
      </button>
    </div>

    <!-- Lớp phủ 1: Đang tải camera -->
    <div v-if="isLoading && !cameraError" class="overlay camera-loading">
      <span class="pulse-ring"></span>
      <AppIcon name="video" :size="30" tone="cyan" />
      <p class="loading-text">Đang kết nối camera...</p>
    </div>

    <!-- Lớp phủ 2: Lỗi camera / Chưa cấp quyền -->
    <div v-if="cameraError" class="overlay camera-error">
      <AppIcon name="alert" :size="32" tone="amber" />
      <p class="error-title">Không thể mở Camera</p>
      <p class="error-desc">{{ cameraError }}</p>
      <button class="btn-retry" type="button" @click="startCamera">
        <AppIcon name="rotate" :size="13" />
        <span>Thử lại</span>
      </button>
    </div>

    <!-- Lớp phủ 3: Xem trước ảnh đã chụp (Snapshot Preview) -->
    <div v-if="snapshotUrl" class="overlay camera-preview">
      <img :src="snapshotUrl" alt="Ảnh chụp" class="preview-img" />
      <div class="preview-actions">
        <span class="preview-badge">ĐÃ CHỤP THÀNH CÔNG</span>
        <div class="btn-row">
          <button class="action-btn action-btn--retake" type="button" @click="retake">
            <AppIcon name="rotate" :size="13" />
            <span>Chụp lại</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Flash effect khi bấm chụp -->
    <div :class="{ 'shutter-flash': isFlashing }"></div>

    <!-- Hidden canvas để crop & xuất snapshot base64 -->
    <canvas ref="hiddenCanvasRef" width="400" height="400" style="display: none;"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import AppIcon from './AppIcon.vue'

const emit = defineEmits(['captured', 'retake'])

const videoRef = ref(null)
const hiddenCanvasRef = ref(null)
const isLoading = ref(true)
const cameraError = ref('')
const snapshotUrl = ref(null)
const isFlashing = ref(false)
const facingMode = ref('user')
const hasMultipleCameras = ref(false)

let mediaStream = null

async function checkCameras() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter((d) => d.kind === 'videoinput')
    hasMultipleCameras.value = videoDevices.length > 1
  } catch {
    hasMultipleCameras.value = false
  }
}

function onVideoLoaded() {
  isLoading.value = false
}

async function startCamera() {
  stopCamera()
  isLoading.value = true
  cameraError.value = ''
  snapshotUrl.value = null

  await nextTick()

  try {
    const constraints = {
      video: {
        facingMode: facingMode.value,
        width: { ideal: 640 },
        height: { ideal: 640 },
      },
      audio: false,
    }

    mediaStream = await navigator.mediaDevices.getUserMedia(constraints)

    if (videoRef.value) {
      videoRef.value.srcObject = mediaStream
      try {
        await videoRef.value.play()
        isLoading.value = false
      } catch {
        // play() có thể cần tương tác của user hoặc event loadeddata
      }
    }
    await checkCameras()
  } catch (err) {
    isLoading.value = false
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      cameraError.value = 'Bạn chưa cấp quyền máy ảnh. Hãy bấm vào icon ổ khóa trên thanh địa chỉ trình duyệt để Cho phép (Allow).'
    } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
      cameraError.value = 'Không tìm thấy thiết bị webcam/camera nào trên máy tính.'
    } else {
      cameraError.value = `Lỗi kết nối camera: ${err.message || err.name}`
    }
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop())
    mediaStream = null
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

function flipCamera() {
  facingMode.value = facingMode.value === 'user' ? 'environment' : 'user'
  startCamera()
}

function takeSnapshot() {
  if (!videoRef.value || !hiddenCanvasRef.value) return

  const video = videoRef.value
  const canvas = hiddenCanvasRef.value
  const ctx = canvas.getContext('2d')

  // Hiệu ứng chớp sáng Shutter Flash
  isFlashing.value = true
  setTimeout(() => {
    isFlashing.value = false
  }, 200)

  // Cắt hình vuông ở giữa video feed
  const vw = video.videoWidth || 400
  const vh = video.videoHeight || 400
  const size = Math.min(vw, vh)
  const startX = (vw - size) / 2
  const startY = (vh - size) / 2

  canvas.width = 400
  canvas.height = 400

  // Camera trước lật gương cho tự nhiên
  if (facingMode.value === 'user') {
    ctx.translate(400, 0)
    ctx.scale(-1, 1)
  }

  ctx.drawImage(video, startX, startY, size, size, 0, 0, 400, 400)

  const dataUrl = canvas.toDataURL('image/png')
  snapshotUrl.value = dataUrl
  emit('captured', dataUrl)

  // Dừng track camera sau khi chụp để giải phóng phần cứng
  stopCamera()
}

function retake() {
  snapshotUrl.value = null
  emit('retake')
  startCamera()
}

onMounted(() => {
  startCamera()
})

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
.camera-wrap {
  position: relative;
  width: 280px;
  height: 280px;
  border: 1px solid rgba(6, 182, 212, 0.4);
  border-radius: 16px;
  background: #000000;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Video element luôn ở background */
.video-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1); /* Lật gương cho camera selfie */
  display: block;
}

.video-feed.is-hidden {
  display: none;
}

/* Các lớp phủ Overlay */
.overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(248, 250, 252, 0.96);
  z-index: 10;
}

/* Lỗi camera */
.camera-error {
  padding: 20px;
  text-align: center;
  gap: 8px;
}

.error-title {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: #dc2626;
}

.error-desc {
  margin: 0;
  font-size: 11px;
  color: #475569;
  line-height: 1.5;
}

.btn-retry {
  margin-top: 8px;
  padding: 6px 14px;
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.16);
  border-radius: 8px;
  color: #334155;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-retry:hover {
  background: rgba(6, 182, 212, 0.2);
  border-color: #06b6d4;
  color: #38bdf8;
}

/* Đang tải camera */
.camera-loading {
  gap: 12px;
}

.pulse-ring {
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 2px solid rgba(6, 182, 212, 0.4);
  animation: pulse-expand 1.8s infinite;
}

@keyframes pulse-expand {
  0% { transform: scale(0.6); opacity: 1; }
  100% { transform: scale(1.6); opacity: 0; }
}

.loading-text {
  margin: 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #0369a1;
}

/* Khung ngắm Viewfinder */
.viewfinder {
  position: absolute;
  inset: 20px;
  border: 1px dashed rgba(6, 182, 212, 0.4);
  border-radius: 12px;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  z-index: 2;
}

.reticle-corner {
  position: absolute;
  width: 14px;
  height: 14px;
  border-color: #06b6d4;
  border-style: solid;
}

.reticle-corner--tl { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
.reticle-corner--tr { top: -1px; right: -1px; border-width: 2px 2px 0 0; }
.reticle-corner--bl { bottom: -1px; left: -1px; border-width: 0 0 2px 2px; }
.reticle-corner--br { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

.reticle-center {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 14px;
  height: 14px;
  margin-top: -7px;
  margin-left: -7px;
  border: 1px solid rgba(6, 182, 212, 0.6);
  border-radius: 50%;
}

.reticle-hint {
  font-family: 'JetBrains Mono', monospace;
  font-size: 8px;
  font-weight: 700;
  color: #38bdf8;
  letter-spacing: 0.08em;
  background: rgba(2, 6, 23, 0.85);
  padding: 3px 8px;
  border-radius: 4px;
  border: 1px solid rgba(6, 182, 212, 0.3);
}

/* Camera Controls */
.camera-controls {
  position: absolute;
  bottom: 12px;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  z-index: 5;
}

.ctrl-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(8px);
  transition: all 0.2s;
}

.ctrl-btn:hover {
  background: rgba(6, 182, 212, 0.3);
  border-color: #06b6d4;
  transform: rotate(90deg);
}

.capture-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: rgba(6, 182, 212, 0.2);
  border: 2px solid #06b6d4;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.capture-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 0 25px rgba(6, 182, 212, 0.7);
  border-color: #38bdf8;
}

.capture-btn__inner {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #06b6d4, #6366f1);
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
}

/* Snapshot Preview */
.camera-preview {
  background: #020617;
  padding: 0;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-actions {
  position: absolute;
  inset: 0;
  background: rgba(2, 6, 23, 0.45);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
}

.preview-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #34d399;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.35);
  padding: 3px 8px;
  border-radius: 999px;
}

.btn-row {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #f1f5f9;
  border-radius: 8px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(8px);
  transition: all 0.2s;
}

.action-btn--retake:hover {
  background: rgba(6, 182, 212, 0.2);
  border-color: #06b6d4;
  color: #38bdf8;
  transform: translateY(-1px);
}

/* Shutter flash */
.shutter-flash {
  position: absolute;
  inset: 0;
  background: #ffffff;
  pointer-events: none;
  z-index: 20;
  animation: flash 0.2s ease-out;
}

@keyframes flash {
  0% { opacity: 0.9; }
  100% { opacity: 0; }
}
</style>
