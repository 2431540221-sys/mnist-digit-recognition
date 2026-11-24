// Composable: usePredict
// Singleton state chia sẻ giữa các component (App.vue, ResultCard, v.v.)
// - results, error, errorInfo, loading, combinedNumber: state phản hồi
//   errorInfo = { stage, passedModel, confidence } cho biết lỗi xảy ra ở bước nào
//   (input | preprocess | model | network | server) và ảnh đã đi qua mô hình CNN chưa
// - predict(dataUrl, mode): gọi backend /predict
// - reset(): xoá state khi đổi mode

import { ref } from 'vue'
import { API_URL } from '../config/api.js'

const results = ref(null)
const error = ref('')
const errorInfo = ref(null)
const loading = ref(false)
const combinedNumber = ref('')

async function predict(dataUrl, mode) {
  error.value = ''
  errorInfo.value = null
  loading.value = true
  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: dataUrl, mode }),
    })
    if (!res.ok) {
      const errData = await res.json().catch(() => null)
      if (errData && errData.error_stage) {
        // Lỗi do backend báo: biết chính xác bước nào và đã qua mô hình chưa
        errorInfo.value = {
          stage: errData.error_stage,
          passedModel: !!errData.passed_model,
          confidence: typeof errData.confidence === 'number' ? errData.confidence : null,
        }
      } else {
        errorInfo.value = { stage: 'server', passedModel: false, confidence: null }
      }
      throw new Error((errData && errData.error) || 'Lỗi từ server')
    }
    const data = await res.json()
    const arr = Array.isArray(data.results) ? data.results : []
    results.value = arr
    if (mode === 'multi') {
      combinedNumber.value =
        (typeof data.number === 'string' && data.number) ||
        arr.map((r) => r.digit).join('')
    } else {
      combinedNumber.value = ''
    }
    return { results: arr, number: combinedNumber.value, mode }
  } catch (err) {
    if (err instanceof TypeError) {
      // fetch() không tới được server (backend tắt / sai địa chỉ)
      errorInfo.value = { stage: 'network', passedModel: false, confidence: null }
      error.value = 'Không kết nối được backend. Kiểm tra đã chạy "python app.py" chưa.'
    } else {
      error.value = err.message
    }
    throw err
  } finally {
    loading.value = false
  }
}

function reset() {
  results.value = null
  error.value = ''
  errorInfo.value = null
  combinedNumber.value = ''
}

// User chon so khac khi model doan nham (vd: model doan 3, user biet la 2).
// Cap nhat digit trong results + tinh lai combinedNumber neu can.
function overrideDigit(index, digit) {
  if (!Array.isArray(results.value)) return
  if (index < 0 || index >= results.value.length) return
  const r = results.value[index]
  r.digit = digit
  // Tắt low_confidence vì user đã chọn
  r.low_confidence = false
  // Cập nhật lại chuỗi số tổng hợp (nếu multi mode)
  combinedNumber.value = results.value.map((x) => x.digit).join('')
}

export function usePredict() {
  return { results, error, errorInfo, loading, combinedNumber, predict, reset, overrideDigit }
}
