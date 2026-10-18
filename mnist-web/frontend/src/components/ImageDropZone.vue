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
        <AppIcon name="upload" :size="32" stroke-width="2" tone="pink" />
      </div>
      <p class="drop__title">Kéo thả ảnh vào đây</p>
      <p class="drop__sub">hoặc <span class="link">chọn file</span> từ máy</p>
      <p class="drop__hint">PNG · JPG · ảnh chữ số nha</p>
    </div>

    <div v-else class="drop__preview">
      <img :src="previewSrc" alt="Ảnh đã chọn" />
      <button class="drop__swap" @click.stop="triggerPicker" type="button">
        <AppIcon name="image" :size="14" />
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
  border: 3px dashed #f9a8d4;
  border-radius: 18px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.drop:hover {
  border-color: #ec4899;
  background: #fdf2f8;
  transform: translateY(-1px);
}

.drop.is-drag {
  border-color: #a855f7;
  border-style: solid;
  background: #f3e8ff;
  transform: scale(1.02);
}

.drop.has-image {
  border-style: solid;
  border-color: #f9a8d4;
  cursor: default;
}

.drop__input {
  display: none;
}

.drop__prompt {
  text-align: center;
  color: #6b5b7a;
  padding: 20px;
}

.drop__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #fce7f3, #f3e8ff);
  border: 2px solid #f9a8d4;
  border-radius: 16px;
  margin-bottom: 12px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.drop__title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 700;
  color: #4a4458;
}

.drop__sub {
  margin: 0 0 12px;
  font-size: 13px;
  color: #8b7a9c;
}

.drop__hint {
  margin: 0;
  font-size: 11px;
  color: #a78bfa;
  letter-spacing: 0.04em;
  font-weight: 600;
}

.link {
  color: #ec4899;
  font-weight: 700;
  text-decoration: underline dotted;
  text-underline-offset: 3px;
}

.drop__preview {
  position: relative;
  width: 100%;
  height: 100%;
  background: #ffffff;
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
  background: linear-gradient(135deg, #f9a8d4, #c4b5fd);
  color: #ffffff;
  border: none;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.3);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.drop__swap:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(236, 72, 153, 0.4);
}
</style>