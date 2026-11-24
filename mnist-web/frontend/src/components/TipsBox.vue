<template>
  <details class="tips">
    <summary class="tips__head">
      <AppIcon name="terminal" :size="14" tone="cyan" />
      <span>Khuyến nghị tối ưu nhận diện</span>
      <AppIcon name="chevron" :size="13" class="tips__chev" />
    </summary>
    <ul class="tips__list">
      <li><strong>Vẽ tập trung:</strong> Căn giữa khung vẽ, kích thước nét từ 12px – 20px.</li>
      <li><strong>Đa chữ số:</strong> Giữ khoảng cách giữa các số $\ge 25\text{px}$ để thuật toán Contour tách chính xác.</li>
      <li><strong>Phong cách số:</strong> Viết số rõ ràng, tránh các nét móc thừa quá phức tạp.</li>
      <li><strong>Tải ảnh / Webcam:</strong> Viết số bằng bút đậm trên giấy trắng, căn số lọt vào giữa khung ngắm hình vuông, giữ đủ ánh sáng và không bị rung tay.</li>
    </ul>
  </details>
</template>

<script setup>
import AppIcon from './AppIcon.vue'
</script>

<style scoped>
.tips {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.92);
  margin-top: 14px;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.tips__head {
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: color 0.15s ease;
}

.tips__head:hover {
  color: #0f172a;
}

.tips__head::-webkit-details-marker {
  display: none;
}

.tips__chev {
  margin-left: auto;
  color: #64748b;
  transition: transform 0.2s ease;
}

.tips[open] .tips__chev {
  transform: rotate(180deg);
  color: #06b6d4;
}

.tips__list {
  margin: 0;
  padding: 4px 16px 12px 30px;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.6;
}

.tips__list strong {
  color: #0f172a;
}

.tips__list li {
  margin-bottom: 4px;
}

.tips__list li::marker {
  color: #06b6d4;
}
</style>
