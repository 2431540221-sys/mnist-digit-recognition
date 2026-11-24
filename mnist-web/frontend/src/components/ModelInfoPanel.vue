<template>
  <section class="card info">
    <div class="info__head">
      <div class="info__title">
        <AppIcon name="info" :size="16" tone="indigo" />
        <span>DỮ LIỆU HUẤN LUYỆN &amp; KIẾN TRÚC CNN</span>
      </div>
      <span class="info__badge">NGUỒN: BACKEND /model-info</span>
    </div>

    <p v-if="loading" class="info__state">Đang tải thông tin mô hình…</p>

    <div v-else-if="failed" class="info__state info__state--err">
      Không lấy được thông tin mô hình (backend chưa chạy?).
      <button class="info__retry" @click="load">Thử lại</button>
    </div>

    <template v-else-if="data">
      <!-- 1. Dữ liệu -->
      <h3 class="info__h">1. Bộ dữ liệu</h3>
      <dl class="kv">
        <div><dt>Tên bộ dữ liệu</dt><dd>{{ data.dataset.name }}</dd></div>
        <div><dt>Lấy từ đâu</dt><dd>{{ data.dataset.source }}</dd></div>
        <div><dt>Loại dữ liệu</dt><dd>{{ data.dataset.data_type }}</dd></div>
        <div><dt>Xử lý trước khi train</dt><dd>{{ data.dataset.preprocessing }}</dd></div>
        <div><dt>Tổng số mẫu</dt><dd>{{ fmt(data.dataset.total_samples) }}</dd></div>
        <div><dt>Số lớp (class)</dt><dd>{{ data.dataset.num_classes }} lớp: {{ data.dataset.classes }}</dd></div>
        <div><dt>Đầu vào mô hình</dt><dd>Ảnh chữ số viết tay {{ data.model.input_shape }} (1 kênh xám)</dd></div>
        <div><dt>Đầu ra mô hình</dt><dd>Vector {{ data.model.output_shape }} xác suất (softmax) — mỗi phần tử là 1 chữ số 0–9</dd></div>
      </dl>

      <div class="split" role="img" :aria-label="`Train ${trainPct}%, validation ${valPct}%`">
        <div class="split__bar">
          <div class="split__train" :style="{ width: trainPct + '%' }">Train {{ trainPct }}%</div>
          <div class="split__val" :style="{ width: valPct + '%' }">Val {{ valPct }}%</div>
        </div>
        <p class="split__legend">
          Train: <strong>{{ fmt(data.dataset.train_samples) }}</strong> mẫu ·
          Validation: <strong>{{ fmt(data.dataset.validation_samples) }}</strong> mẫu
          (<strong>{{ valPct }}%</strong> tổng dữ liệu).
        </p>
        <p class="split__note">{{ data.dataset.split_note }}</p>
      </div>

      <!-- 2. Kiến trúc -->
      <h3 class="info__h">2. Kiến trúc CNN</h3>
      <div class="chips">
        <span class="chip"><strong>{{ data.model.total_layers }}</strong> lớp Keras</span>
        <span class="chip"><strong>{{ data.model.layer_counts.Conv2D }}</strong> Conv2D</span>
        <span class="chip"><strong>{{ data.model.layer_counts.MaxPooling2D }}</strong> MaxPooling</span>
        <span class="chip"><strong>{{ data.model.layer_counts.BatchNormalization }}</strong> BatchNorm</span>
        <span class="chip"><strong>{{ data.model.layer_counts.Dropout }}</strong> Dropout</span>
        <span class="chip"><strong>{{ data.model.layer_counts.Dense }}</strong> Dense</span>
        <span class="chip"><strong>{{ fmt(data.model.total_params) }}</strong> tham số</span>
      </div>

      <div class="table-wrap">
        <table class="tbl">
          <thead>
            <tr>
              <th>#</th>
              <th>Lớp</th>
              <th>Cấu hình / phép tính</th>
              <th>Kích thước đầu ra</th>
              <th>Tham số</th>
              <th>Hàm kích hoạt</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(l, i) in data.model.layers" :key="l.name" :class="{ 'is-conv': l.type === 'Conv2D', 'is-dense': l.type === 'Dense' }">
              <td class="mono">{{ i + 1 }}</td>
              <td>{{ l.label }}<span class="mono dim"> · {{ l.name }}</span></td>
              <td>{{ l.detail }}</td>
              <td class="mono">{{ l.output_shape }}</td>
              <td class="mono">{{ fmt(l.params) }}</td>
              <td class="mono">{{ l.activation ? l.activation.toUpperCase() : '—' }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="4">Tổng (huấn luyện được {{ fmt(data.model.trainable_params) }} · không huấn luyện {{ fmt(data.model.non_trainable_params) }})</td>
              <td class="mono">{{ fmt(data.model.total_params) }}</td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- 3. Huấn luyện -->
      <h3 class="info__h">3. Cấu hình huấn luyện</h3>
      <dl class="kv">
        <div><dt>Optimizer</dt><dd>{{ data.training.optimizer }}</dd></div>
        <div><dt>Hàm mất mát</dt><dd>{{ data.training.loss }}</dd></div>
        <div><dt>Batch size / Epoch tối đa</dt><dd>{{ data.training.batch_size }} / {{ data.training.max_epochs }}</dd></div>
        <div><dt>Data augmentation</dt><dd>{{ data.training.augmentation }}</dd></div>
        <div><dt>Callbacks</dt><dd>{{ data.training.callbacks }}</dd></div>
      </dl>
    </template>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from './AppIcon.vue'
import { API_MODEL_INFO_URL } from '../config/api.js'

const data = ref(null)
const loading = ref(true)
const failed = ref(false)

const fmt = (n) => Number(n).toLocaleString('vi-VN')

const valPct = computed(() =>
  data.value ? ((data.value.dataset.validation_samples / data.value.dataset.total_samples) * 100).toFixed(2) : '0'
)
const trainPct = computed(() =>
  data.value ? ((data.value.dataset.train_samples / data.value.dataset.total_samples) * 100).toFixed(2) : '0'
)

async function load() {
  loading.value = true
  failed.value = false
  try {
    const res = await fetch(API_MODEL_INFO_URL)
    if (!res.ok) throw new Error('bad status')
    data.value = await res.json()
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.info {
  margin-top: 20px;
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 22px;
  padding: 22px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.info__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.info__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: 0.06em;
}

.info__badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 9px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #4f46e5;
}

.info__h {
  margin: 20px 0 10px;
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
}

.info__state {
  margin: 16px 0 0;
  font-size: 12px;
  color: #64748b;
}

.info__state--err {
  color: #b91c1c;
}

.info__retry {
  margin-left: 8px;
  padding: 3px 10px;
  border: 1px solid rgba(15, 23, 42, 0.16);
  border-radius: 6px;
  background: #ffffff;
  color: #334155;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

/* key-value */
.kv {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 20px;
  margin: 0;
}

.kv > div {
  padding: 8px 12px;
  background: #f8fafc;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 10px;
}

.kv dt {
  font-size: 10px;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.kv dd {
  margin: 2px 0 0;
  font-size: 12px;
  color: #0f172a;
  line-height: 1.5;
}

/* thanh chia train/validation */
.split {
  margin-top: 14px;
}

.split__bar {
  display: flex;
  height: 28px;
  border-radius: 8px;
  overflow: hidden;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 700;
  color: #ffffff;
}

.split__train,
.split__val {
  display: flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.split__train { background: linear-gradient(90deg, #4f46e5, #0891b2); }
.split__val { background: #f59e0b; }

.split__legend {
  margin: 8px 0 0;
  font-size: 12px;
  color: #334155;
}

.split__note {
  margin: 4px 0 0;
  font-size: 11px;
  color: #64748b;
}

/* chips */
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(6, 182, 212, 0.08);
  border: 1px solid rgba(6, 182, 212, 0.3);
  font-size: 11px;
  color: #334155;
}

.chip strong {
  color: #0369a1;
  font-family: 'JetBrains Mono', monospace;
}

/* bảng lớp */
.table-wrap {
  overflow-x: auto;
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 12px;
}

.tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  min-width: 720px;
}

.tbl th {
  text-align: left;
  padding: 8px 10px;
  background: #f1f5f9;
  color: #475569;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  white-space: nowrap;
}

.tbl td {
  padding: 7px 10px;
  border-top: 1px solid rgba(15, 23, 42, 0.06);
  color: #334155;
}

.tbl tr.is-conv td { background: rgba(6, 182, 212, 0.06); }
.tbl tr.is-dense td { background: rgba(99, 102, 241, 0.06); }

.tbl tfoot td {
  background: #f1f5f9;
  font-weight: 700;
  color: #0f172a;
}

.mono { font-family: 'JetBrains Mono', monospace; font-size: 11px; }
.dim { color: #94a3b8; }

@media (max-width: 720px) {
  .kv { grid-template-columns: 1fr; }
  .info { padding: 16px; }
}
</style>
