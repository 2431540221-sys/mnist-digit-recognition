<template>
  <div class="tabs" role="tablist" aria-label="Chế độ dự đoán">
    <button
      role="tab"
      :aria-selected="currentMode === 'single'"
      :class="{ tab: true, 'is-active': currentMode === 'single' }"
      @click="setMode('single')"
    >
      <span class="tab__badge">1</span>
      <span>Đơn chữ số</span>
    </button>
    <button
      role="tab"
      :aria-selected="currentMode === 'multi'"
      :class="{ tab: true, 'is-active': currentMode === 'multi' }"
      @click="setMode('multi')"
    >
      <span class="tab__badge">123</span>
      <span>Đa chữ số</span>
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
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  padding: 4px;
  margin-bottom: 18px;
  gap: 4px;
  backdrop-filter: blur(10px);
}

.tab {
  flex: 1;
  padding: 10px 14px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.tab__badge {
  background: rgba(15, 23, 42, 0.04);
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 6px;
  padding: 2px 7px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  color: #334155;
  letter-spacing: 0.04em;
  transition: all 0.2s;
}

.tab:hover:not(.is-active) {
  background: rgba(15, 23, 42, 0.04);
  color: #0f172a;
}

.tab.is-active {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.9) 0%, rgba(6, 182, 212, 0.85) 100%);
  color: #ffffff;
  border-color: transparent;
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35);
}

.tab.is-active .tab__badge {
  background: rgba(0, 0, 0, 0.3);
  color: #67e8f9;
  border-color: rgba(6, 182, 212, 0.4);
}

.tab:focus-visible {
  outline: 2px solid #06b6d4;
  outline-offset: 2px;
}
</style>
