<template>
  <div
    class="drop"
    :class="{ 'is-drag': isDragging, 'has-image': Boolean(previewSrc) }"
    @dragenter.prevent="isDragging = true"
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="onDrop"
    @click="onClickZone"
  >
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      class="drop__input"
      @change="onFileChange"
    />

    <div v-if="!previewSrc" class="drop__prompt">
      <div class="drop__icon">
        <AppIcon name="upload" :size="28" stroke-width="2" tone="cyan" />
      </div>
      <p class="drop__title">Kéo & thả ảnh vào đây</p>
      <p class="drop__sub">hoặc <span class="link">chọn file</span> từ thiết bị</p>
      <p class="drop__hint">PNG · JPG · Tối ưu nền trắng số đen</p>
    </div>

    <div v-else class="drop__preview">
      <img :src="previewSrc" alt="Ảnh đã chọn" />
      <button class="drop__swap" @click.stop="triggerPicker" type="button">
        <AppIcon name="image" :size="13" />
        <span>Đổi ảnh</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppIcon from './AppIcon.vue'
import { useAppState } from '../composables/useAppState.js'

const emit = defineEmits(['fileSelected'])
const { uploadedImageDataUrl } = useAppState()

const fileInputRef = ref(null)
const isDragging = ref(false)
const previewSrc = uploadedImageDataUrl

function onClickZone() {
  if (!previewSrc.value) triggerPicker()
}

function triggerPicker() {
  fileInputRef.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (file) readFile(file)
  e.target.value = ''
}

function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) readFile(file)
}

function readFile(file) {
  const reader = new FileReader()
  reader.onload = (ev) => {
    const dataUrl = ev.target.result
    uploadedImageDataUrl.value = dataUrl
    emit('fileSelected', dataUrl)
  }
  reader.readAsDataURL(file)
}
</script>

<style scoped>
.drop {
  position: relative;
  width: 280px;
  height: 280px;
  border: 1px dashed rgba(6, 182, 212, 0.4);
  border-radius: 16px;
  background: rgba(241, 245, 249, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: inset 0 0 20px rgba(15, 23, 42, 0.10);
}

.drop:hover {
  border-color: #06b6d4;
  background: rgba(6, 182, 212, 0.05);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.15), inset 0 0 20px rgba(15, 23, 42, 0.10);
}

.drop.is-drag {
  border-color: #818cf8;
  border-style: solid;
  background: rgba(99, 102, 241, 0.15);
  transform: scale(1.02);
}

.drop.has-image {
  border-style: solid;
  border-color: rgba(99, 102, 241, 0.4);
  cursor: default;
}

.drop__input {
  display: none;
}

.drop__prompt {
  text-align: center;
  color: #94a3b8;
  padding: 20px;
}

.drop__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-radius: 14px;
  margin-bottom: 12px;
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
}

.drop__title {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
}

.drop__sub {
  margin: 0 0 10px;
  font-size: 12px;
  color: #94a3b8;
}

.drop__hint {
  margin: 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  color: #64748b;
  letter-spacing: 0.04em;
}

.link {
  color: #0369a1;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.drop__preview {
  position: relative;
  width: 100%;
  height: 100%;
  background: #f8fafc;
  border-radius: 14px;
  overflow: hidden;
}

.drop__preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 14px;
}

.drop__swap {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.16);
  color: #0f172a;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(8px);
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.15s ease;
}

.drop__swap:hover {
  background: #e2e8f0;
  border-color: #06b6d4;
  color: #0369a1;
  transform: translateY(-1px);
}
</style>
