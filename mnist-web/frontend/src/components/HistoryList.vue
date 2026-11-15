<template>
  <div v-if="history.length" class="history">
    <div class="history__head">
      <span class="history__title">
        <AppIcon name="history" :size="14" tone="indigo" />
        <span>NHẬT KÝ SUY LUẬN ({{ history.length }})</span>
      </span>
      <button class="history__dl" @click="download" type="button" title="Xuất dữ liệu JSON">
        <AppIcon name="download" :size="12" />
        <span>Xuất JSON</span>
      </button>
    </div>
    <ul class="history__list">
      <li v-for="(entry, i) in history" :key="i" class="history__item">
        <span class="history__time">{{ entry.time }}</span>
        <span class="history__mode" :class="`history__mode--${entry.mode}`">
          {{ entry.mode === 'single' ? 'ĐƠN' : 'ĐA SỐ' }}
        </span>
        <span class="history__digits">
          {{ entry.digits.join('') }}
        </span>
      </li>
    </ul>
  </div>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
import { useHistory } from '../composables/useHistory.js'
const { history, download } = useHistory()
</script>

<style scoped>
.history {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.75);
  margin-top: 16px;
  overflow: hidden;
  backdrop-filter: blur(12px);
}

.history__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(2, 6, 23, 0.5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.history__title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  color: #818cf8;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.05em;
}

.history__dl {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #cbd5e1;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.history__dl:hover {
  background: rgba(6, 182, 212, 0.15);
  border-color: rgba(6, 182, 212, 0.4);
  color: #38bdf8;
  transform: translateY(-1px);
}

.history__list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 200px;
  overflow-y: auto;
}

.history__list::-webkit-scrollbar {
  width: 5px;
}

.history__list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
}

.history__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 14px;
  font-size: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s;
}

.history__item:last-child {
  border-bottom: none;
}

.history__item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.history__time {
  font-family: 'JetBrains Mono', monospace;
  color: #64748b;
  font-size: 11px;
  min-width: 70px;
}

.history__mode {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.04em;
}

.history__mode--single {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.history__mode--multi {
  background: rgba(6, 182, 212, 0.15);
  color: #38bdf8;
  border: 1px solid rgba(6, 182, 212, 0.3);
}

.history__digits {
  font-family: 'JetBrains Mono', monospace;
  color: #f1f5f9;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.05em;
  margin-left: auto;
}
</style>
