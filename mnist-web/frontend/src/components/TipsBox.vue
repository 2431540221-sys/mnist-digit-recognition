<template>
  <details class="tips">
    <summary class="tips__head">
      <AppIcon name="info" :size="16" tone="purple" />
      <span>Mẹo để mình đoán chuẩn hơn nè</span>
      <AppIcon name="chevron" :size="14" class="tips__chev" />
    </summary>
    <ul class="tips__list">
      <li>Viết rõ từng số, không để 2 số dính nhau.</li>
      <li>Nét đậm, đơn giản, đừng thêm nét thừa.</li>
      <li>Viết số đủ to, chiếm phần lớn khung vẽ.</li>
      <li>Canh số nằm giữa, không sát mép trên/dưới.</li>
      <li>Ảnh tải lên nên nền trắng, số màu đen nha.</li>
    </ul>
  </details>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
</script>

<style scoped>
.tips {
  border: 2px solid #fbcfe8;
  border-radius: 14px;
  background: #fdf2f8;
  margin-bottom: 18px;
  overflow: hidden;
}

.tips__head {
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #6b5b7a;
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tips__head::-webkit-details-marker {
  display: none;
}

.tips__chev {
  margin-left: auto;
  color: #f9a8d4;
  transition: transform 0.2s;
}

.tips[open] .tips__chev {
  transform: rotate(180deg);
}

.tips__list {
  margin: 0;
  padding: 4px 18px 12px 32px;
  color: #6b5b7a;
  font-size: 13px;
  line-height: 1.7;
}

.tips__list li::marker {
  color: #f9a8d4;
}
</style>