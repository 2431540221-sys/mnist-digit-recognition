<template>
  <component
    :is="icon"
    :size="size"
    :stroke-width="strokeWidth"
    :class="['icon', `icon--${tone}`]"
    aria-hidden="true"
  />
</template>

<script setup>
import { computed } from 'vue'
import {
  Sparkles,
  Pencil,
  PencilLine,
  Eraser,
  Trash2,
  Undo2,
  Redo2,
  Image as ImageIcon,
  Upload,
  Download,
  AlertCircle,
  ChevronDown,
  History,
  Wand2,
  Brain,
  Bot,
  Heart,
  Check,
  X,
  Star,
  CircleHelp,
  Info,
  Cpu,
  Layers,
  Terminal,
  Activity,
  Camera,
  RotateCcw,
  Video,
} from 'lucide-vue-next'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 18 },
  strokeWidth: { type: [Number, String], default: 2 },
  tone: {
    type: String,
    default: 'default',
  },
})

const map = {
  sparkles: Sparkles,
  pencil: Pencil,
  'pencil-line': PencilLine,
  eraser: Eraser,
  trash: Trash2,
  undo: Undo2,
  redo: Redo2,
  image: ImageIcon,
  upload: Upload,
  download: Download,
  alert: AlertCircle,
  chevron: ChevronDown,
  history: History,
  wand: Wand2,
  brain: Brain,
  bot: Bot,
  heart: Heart,
  check: Check,
  close: X,
  star: Star,
  help: CircleHelp,
  info: Info,
  cpu: Cpu,
  layers: Layers,
  terminal: Terminal,
  activity: Activity,
  camera: Camera,
  video: Video,
  rotate: RotateCcw,
}

const icon = computed(() => map[props.name] || Sparkles)
</script>

<style scoped>
.icon {
  flex-shrink: 0;
  vertical-align: middle;
  display: inline-block;
}

.icon--default { color: currentColor; }
.icon--cyan { color: #06b6d4; }
.icon--indigo { color: #6366f1; }
.icon--emerald { color: #10b981; }
.icon--amber { color: #f59e0b; }
.icon--pink { color: #ec4899; }
.icon--purple { color: #a855f7; }
.icon--soft { color: #94a3b8; }
</style>
