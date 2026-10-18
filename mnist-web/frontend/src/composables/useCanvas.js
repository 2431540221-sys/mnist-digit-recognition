// Composable: useCanvas
// Gom toàn bộ logic vẽ tay (mouse + touch) vào 1 nơi
// - attach(canvasRef): gắn event lên canvas element
// - clear(): xóa canvas
// - toDataURL(): lấy dataURL từ canvas
// - undo() / redo(): hoàn tác / làm lại (snapshot trước/sau mỗi stroke)
// - setBrushSize(px): đổi cỡ nét vẽ
// - canUndo / canRedo: ref reactive cho UI disable/enable

import { ref, reactive } from 'vue'

const CANVAS_SIZE = 280
const BG_COLOR = 'black'
const BRUSH_COLOR = 'white'
const DEFAULT_BRUSH = 15

export function useCanvas() {
  let ctx = null
  let canvasEl = null
  let drawing = false
  let currentBrush = DEFAULT_BRUSH

  // Undo/redo stacks lưu ImageData
  const undoStack = []
  const redoStack = []
  const MAX_HISTORY = 30

  const canUndo = ref(false)
  const canRedo = ref(false)

  function _refreshButtons() {
    canUndo.value = undoStack.length > 0
    canRedo.value = redoStack.length > 0
  }

  function _pushHistory() {
    if (!ctx || !canvasEl) return
    if (undoStack.length >= MAX_HISTORY) undoStack.shift()
    undoStack.push(ctx.getImageData(0, 0, CANVAS_SIZE, CANVAS_SIZE))
    redoStack.length = 0
    _refreshButtons()
  }

  function _getPos(e) {
    const rect = canvasEl.getBoundingClientRect()
    return { x: e.clientX - rect.left, y: e.clientY - rect.top }
  }

  function _attachMouse() {
    canvasEl.addEventListener('mousedown', start)
    canvasEl.addEventListener('mousemove', draw)
    canvasEl.addEventListener('mouseup', stop)
    canvasEl.addEventListener('mouseleave', stop)
  }

  function _attachTouch() {
    canvasEl.addEventListener('touchstart', (e) => {
      e.preventDefault()
      start(e.touches[0])
    })
    canvasEl.addEventListener('touchmove', (e) => {
      e.preventDefault()
      draw(e.touches[0])
    })
    canvasEl.addEventListener('touchend', (e) => {
      e.preventDefault()
      stop()
    })
  }

  function attach(el) {
    if (!el) return
    canvasEl = el
    ctx = el.getContext('2d')
    resetStyle()
    undoStack.length = 0
    redoStack.length = 0
    _refreshButtons()
    _attachMouse()
    _attachTouch()
  }

  function start(e) {
    if (!ctx) return
    // Lưu snapshot TRƯỚC khi vẽ stroke mới
    _pushHistory()
    drawing = true
    const { x, y } = _getPos(e)
    ctx.strokeStyle = BRUSH_COLOR
    ctx.lineWidth = currentBrush
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    ctx.beginPath()
    ctx.moveTo(x, y)
  }

  function draw(e) {
    if (!drawing || !ctx) return
    const { x, y } = _getPos(e)
    ctx.lineTo(x, y)
    ctx.stroke()
  }

  function stop() {
    drawing = false
  }

  function resetStyle() {
    if (!ctx) return
    ctx.fillStyle = BG_COLOR
    ctx.fillRect(0, 0, CANVAS_SIZE, CANVAS_SIZE)
  }

  function clear() {
    if (!ctx) return
    _pushHistory() // lưu trạng thái trước khi xóa để undo được
    resetStyle()
  }

  function undo() {
    if (!ctx || undoStack.length === 0) return
    // Lưu trạng thái hiện tại vào redo trước khi restore
    redoStack.push(ctx.getImageData(0, 0, CANVAS_SIZE, CANVAS_SIZE))
    const snap = undoStack.pop()
    ctx.putImageData(snap, 0, 0)
    _refreshButtons()
  }

  function redo() {
    if (!ctx || redoStack.length === 0) return
    undoStack.push(ctx.getImageData(0, 0, CANVAS_SIZE, CANVAS_SIZE))
    const snap = redoStack.pop()
    ctx.putImageData(snap, 0, 0)
    _refreshButtons()
  }

  function setBrushSize(px) {
    currentBrush = Math.max(1, Math.min(80, Number(px) || DEFAULT_BRUSH))
  }

  function toDataURL(el) {
    const target = el || canvasEl
    return target ? target.toDataURL('image/png') : null
  }

  return {
    attach,
    clear,
    toDataURL,
    resetStyle,
    undo,
    redo,
    setBrushSize,
    canUndo,
    canRedo,
  }
}