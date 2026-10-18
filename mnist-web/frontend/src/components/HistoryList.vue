<template>
  <div v-if="history.length" class="history">
    <div class="history__head">
      <span class="history__title">
        <AppIcon name="history" :size="14" />
        <span>Lịch sử ({{ history.length }})</span>
      </span>
      <button class="history__dl" @click="download" type="button">
        <AppIcon name="download" :size="13" />
        <span>Tải xuống</span>
      </button>
    </div>
    <ul class="history__list">
      <li v-for="(entry, i) in history" :key="i" class="history__item">
        <span class="history__time">{{ entry.time }}</span>
        <span class="history__mode">
          {{ entry.mode === 'single' ? '1 số' : 'Nhiều số' }}
        </span>
        <span class="history__digits">
          {{ entry.digits.join(', ') }}
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
  border: 2px solid #fbcfe8;
  border-radius: 16px;
  background: #ffffff;
  margin-top: 20px;
  overflow: hidden;
}

.history__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #fdf2f8, #faf5ff);
  border-bottom: 2px solid #fbcfe8;
}

.history__title {
  font-size: 13px;
  font-weight: 700;
  color: #a855f7;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.history__dl {
  background: #ffffff;
  border: 1.5px solid #f9a8d4;
  border-radius: 999px;
  color: #ec4899;
  font-size: 12px;
  font-weight: 700;
  padding: 5px 12px;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.history__dl:hover {
  background: #fdf2f8;
  transform: translateY(-1px);
}

.history__list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 220px;
  overflow-y: auto;
}

.history__item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 16px;
  font-size: 13px;
  border-bottom: 1px solid #fdf2f8;
}

.history__item:last-child {
  border-bottom: none;
}

.history__item:hover {
  background: #fdf2f8;
}

.history__time {
  color: #a78bfa;
  font-size: 11px;
  min-width: 100px;
  font-weight: 500;
}

.history__mode {
  background: linear-gradient(135deg, #fce7f3, #f3e8ff);
  color: #a855f7;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}

.history__digits {
  color: #ec4899;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
</style>