<template>
  <div class="page">
    <div class="doodles" aria-hidden="true">
      <span class="doodle d1">✏️</span>
      <span class="doodle d2">🌸</span>
      <span class="doodle d3">⭐</span>
      <span class="doodle d4">💖</span>
      <span class="doodle d5">✨</span>
      <span class="doodle d6">🌷</span>
      <span class="doodle d7">💫</span>
    </div>

    <main class="card">
      <header class="header">
        <div class="header__row">
          <span class="header__icon" aria-hidden="true">
            <AppIcon name="brain" :size="34" stroke-width="2.2" tone="pink" />
          </span>
          <h1 class="header__title">Nhận diện chữ số</h1>
        </div>
        <p class="header__lede">
          Vẽ hoặc tải ảnh lên — AI sẽ đoán giúp bạn ♡
        </p>
      </header>

      <ModeTabs />

      <section class="workspace">
        <div class="seg" role="tablist" aria-label="Chọn cách nhập">
          <button
            role="tab"
            :aria-selected="inputTab === 'draw'"
            :class="{ seg__btn: true, 'is-active': inputTab === 'draw' }"
            @click="setInputTab('draw')"
          >
            <AppIcon name="pencil-line" :size="16" />
            <span>Vẽ tay</span>
          </button>
          <button
            role="tab"
            :aria-selected="inputTab === 'upload'"
            :class="{ seg__btn: true, 'is-active': inputTab === 'upload' }"
            @click="setInputTab('upload')"
          >
            <AppIcon name="upload" :size="16" />
            <span>Tải ảnh</span>
          </button>
        </div>

        <div class="stage">
          <DrawingCanvas v-if="inputTab === 'draw'" />
          <ImageDropZone v-else @fileSelected="onUploadFile" />
        </div>

        <BrushToolbar v-if="inputTab === 'draw'" />
      </section>

      <ActionButtons />

      <TipsBox />

      <section v-if="results && results.length" class="results">
        <CombinedResult />
        <ResultCard
          v-for="(result, index) in results"
          :key="index"
          :result="result"
          :index="index"
          :multi="currentMode === 'multi'"
          @select="onSelectAlternative"
        />
      </section>

      <ErrorBanner />

      <HistoryList />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppIcon from './components/AppIcon.vue'
import ModeTabs from './components/ModeTabs.vue'
import DrawingCanvas from './components/DrawingCanvas.vue'
import ImageDropZone from './components/ImageDropZone.vue'
import BrushToolbar from './components/BrushToolbar.vue'
import ActionButtons from './components/ActionButtons.vue'
import TipsBox from './components/TipsBox.vue'
import ResultCard from './components/ResultCard.vue'
import CombinedResult from './components/CombinedResult.vue'
import ErrorBanner from './components/ErrorBanner.vue'
import HistoryList from './components/HistoryList.vue'

import { useAppState } from './composables/useAppState.js'
import { usePredict } from './composables/usePredict.js'

const { currentMode, setUploadedImage } = useAppState()
const { results, overrideDigit } = usePredict()

const inputTab = ref('draw')

function setInputTab(tab) {
  inputTab.value = tab
  setUploadedImage(null)
}

function onUploadFile(dataUrl) {
  setUploadedImage(dataUrl)
}

function onSelectAlternative({ index, digit }) {
  overrideDigit(index, digit)
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

*,
*::before,
*::after {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  padding: 0;
  font-family: 'Quicksand', system-ui, -apple-system, 'Segoe UI', sans-serif;
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  color: #4a4458;
  background: #fdf2f8;
}

button {
  font-family: inherit;
}
</style>

<style scoped>
.page {
  position: relative;
  min-height: 100vh;
  padding: 40px 16px;
  display: flex;
  justify-content: center;
  overflow: hidden;
  background-color: #fdf2f8;
  background-image: url('/pencil-pattern.svg'),
    radial-gradient(ellipse at top left, #fce7f3 0%, transparent 60%),
    radial-gradient(ellipse at bottom right, #e0e7ff 0%, transparent 60%),
    linear-gradient(135deg, #fdf2f8 0%, #f5f3ff 50%, #ecfeff 100%);
  background-size: 320px 320px, auto, auto, auto;
  background-repeat: repeat, no-repeat, no-repeat, no-repeat;
  background-attachment: fixed;
}

/* Doodle trôi nổi */
.doodles {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.doodle {
  position: absolute;
  font-size: 28px;
  opacity: 0.55;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.05));
  animation: bob 8s ease-in-out infinite;
}

.d1 { top: 8%; left: 6%; animation-delay: 0s; font-size: 32px; }
.d2 { top: 18%; right: 8%; animation-delay: -2s; font-size: 24px; }
.d3 { top: 45%; left: 4%; animation-delay: -4s; font-size: 22px; }
.d4 { top: 70%; right: 6%; animation-delay: -1s; font-size: 26px; }
.d5 { bottom: 12%; left: 12%; animation-delay: -3s; font-size: 28px; }
.d6 { top: 30%; right: 15%; animation-delay: -5s; font-size: 20px; }
.d7 { bottom: 25%; right: 18%; animation-delay: -6s; font-size: 24px; }

@keyframes bob {
  0%, 100% { transform: translateY(0) rotate(-6deg); }
  50% { transform: translateY(-14px) rotate(6deg); }
}

.card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 560px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 2px solid #fbcfe8;
  border-radius: 28px;
  padding: 32px 28px;
  box-shadow:
    0 4px 0 0 #fce7f3,
    0 12px 32px rgba(236, 72, 153, 0.12),
    0 24px 48px rgba(168, 85, 247, 0.08);
}

/* Header */
.header {
  margin-bottom: 24px;
  text-align: center;
}

.header__row {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.header__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  background: linear-gradient(135deg, #fce7f3, #f3e8ff);
  border: 2px solid #f9a8d4;
  border-radius: 14px;
  animation: wiggle 3s ease-in-out infinite;
}

@keyframes wiggle {
  0%, 100% { transform: rotate(-6deg); }
  50% { transform: rotate(6deg); }
}

.header__title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(135deg, #ec4899, #a855f7, #f472b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.01em;
}

.header__lede {
  margin: 0;
  color: #8b7a9c;
  font-size: 14px;
  font-weight: 500;
}

/* Workspace */
.workspace {
  background: linear-gradient(135deg, #fef3f9 0%, #f3e8ff 100%);
  border: 2px dashed #f9a8d4;
  border-radius: 22px;
  padding: 18px;
  margin-bottom: 18px;
}

/* Segmented control - cute */
.seg {
  display: flex;
  background: #ffffff;
  border: 2px solid #fbcfe8;
  border-radius: 16px;
  padding: 4px;
  margin-bottom: 14px;
  gap: 4px;
}

.seg__btn {
  flex: 1;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: #a78bfa;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.seg__btn:hover:not(.is-active) {
  background: #fdf2f8;
  color: #ec4899;
}

.seg__btn.is-active {
  background: linear-gradient(135deg, #f9a8d4, #c4b5fd);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.25);
}

.seg__btn.is-active :deep(.icon) {
  color: #ffffff;
}

.seg__btn:focus-visible {
  outline: 2px solid #ec4899;
  outline-offset: 2px;
}

.stage {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 280px;
  padding: 4px 0;
}

.results {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

@media (max-width: 520px) {
  .page {
    padding: 20px 12px;
  }
  .card {
    padding: 24px 18px;
    border-radius: 24px;
  }
  .header__title {
    font-size: 22px;
  }
  .doodle {
    font-size: 20px !important;
  }
}

@media (prefers-reduced-motion: reduce) {
  .doodle, .header__icon { animation: none; }
}
</style>