// Composable: useAppState
// State dùng chung giữa nhiều component:
// - currentMode: 'single' | 'multi'
// - uploadedImageDataUrl: ảnh upload từ máy (null nếu đang dùng canvas)
// - canvasRef: ref tới <canvas> element (do DrawingCanvas quản lý)

import { ref } from 'vue'
import { useCanvas } from './useCanvas.js'
import { usePredict } from './usePredict.js'

const currentMode = ref('single')
const uploadedImageDataUrl = ref(null)
const canvasEl = ref(null)

const { clear: clearCanvasDraw, toDataURL, attach: attachCanvas } = useCanvas()

function setMode(mode) {
  currentMode.value = mode
  uploadedImageDataUrl.value = null
  clearCanvasDraw()
  usePredict().reset()
}

function setUploadedImage(dataUrl) {
  uploadedImageDataUrl.value = dataUrl
}

function clearAll() {
  uploadedImageDataUrl.value = null
  clearCanvasDraw()
  usePredict().reset()
}

function setCanvasRef(el) {
  canvasEl.value = el
  attachCanvas(el)
}

// Trả về 1 instance duy nhất (singleton) - import ở đâu cũng dùng chung state
let _instance = null
export function useAppState() {
  if (!_instance) {
    _instance = { currentMode, uploadedImageDataUrl, canvasEl, setMode, setUploadedImage, clearAll, setCanvasRef, toDataURL }
  }
  return _instance
}
