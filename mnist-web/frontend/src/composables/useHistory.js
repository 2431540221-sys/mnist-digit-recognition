// Composable: useHistory
// Singleton state lưu lịch sử dự đoán + hàm tải xuống file .txt

import { ref } from 'vue'

const history = ref([])

function add(entry) {
  history.value.unshift(entry)
}

function download() {
  if (!history.value.length) return
  const lines = history.value.map((entry) => {
    const mode = entry.mode === 'single' ? '1 số' : 'Nhiều số'
    return `[${entry.time}] Chế độ: ${mode} | Kết quả: ${entry.digits.join(', ')}`
  })
  const content =
    'Lịch sử Dự Đoán Chữ Số Viết Tay\n' +
    '='.repeat(50) +
    '\n' +
    lines.join('\n')
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'lich_su_du_doan.txt'
  a.click()
  URL.revokeObjectURL(url)
}

export function useHistory() {
  return { history, add, download }
}
