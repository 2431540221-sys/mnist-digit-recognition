<template>
  <div class="tabs" role="tablist" aria-label="Chế độ dự đoán">
    <button
      role="tab"
      :aria-selected="currentMode === 'single'"
      :class="{ tab: true, 'is-active': currentMode === 'single' }"
      @click="setMode('single')"
    >
      <span class="tab__badge">1</span>
      <span>chữ số</span>
    </button>
    <button
      role="tab"
      :aria-selected="currentMode === 'multi'"
      :class="{ tab: true, 'is-active': currentMode === 'multi' }"
      @click="setMode('multi')"
    >
      <span class="tab__badge">123</span>
      <span>Nhiều số</span>
    </button>
  </div>
</template>

<script setup>
import { useAppState } from '../composables/useAppState.js'
const { currentMode, setMode } = useAppState()
</script>

<style scoped>
.tabs {
  display: flex;
  background: #fdf2f8;
  border: 2px solid #fbcfe8;
  border-radius: 16px;
  padding: 4px;
  margin-bottom: 18px;
  gap: 4px;
}

.tab {
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

.tab__badge {
  background: #ffffff;
  border: 1.5px solid #f9a8d4;
  border-radius: 8px;
  padding: 1px 6px;
  font-size: 11px;
  font-weight: 700;
  color: #ec4899;
  letter-spacing: 0.04em;
}

.tab:hover:not(.is-active) {
  background: #fce7f3;
}

.tab.is-active {
  background: linear-gradient(135deg, #f9a8d4, #c4b5fd);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(236, 72, 153, 0.25);
}

.tab.is-active .tab__badge {
  background: rgba(255, 255, 255, 0.3);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.5);
}

.tab:focus-visible {
  outline: 2px solid #ec4899;
  outline-offset: 2px;
}
</style>