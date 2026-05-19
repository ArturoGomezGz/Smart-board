<script setup>
import { ref, onMounted } from 'vue'
import { useCamera } from '../composables/useCamera'

const MODES = [
  { id: 'diagram',    label: '📐 Diagrama',     prompt: 'Convierte este diagrama a Mermaid.' },
  { id: 'transcribe', label: '📝 Transcribir',   prompt: 'Transcribe todo el texto del pizarrón.' },
  { id: 'explain',    label: '💡 Explicar',      prompt: 'Explica el contenido del pizarrón.' },
  { id: 'review',     label: '🔍 Revisar',       prompt: 'Revisa y corrige el contenido.' },
  { id: 'code',       label: '💻 Código',        prompt: 'Genera el código equivalente.' },
  { id: 'describe',   label: '👁 Describir',     prompt: 'Describe todo lo que ves.' },
]

const emit = defineEmits(['capture'])

const { cameras, selectedCamera, isActive, loadCameras, startCamera, captureFrame } = useCamera()

const videoEl = ref(null)
const canvasEl = ref(null)
const flashEl = ref(null)
const flashing = ref(false)
const activeMode = ref('diagram')
const customPrompt = ref('')

const selectedMode = () => MODES.find(m => m.id === activeMode.value)
const finalPrompt = () => customPrompt.value.trim() || selectedMode().prompt

onMounted(loadCameras)

async function handleStart() {
  try {
    await startCamera(videoEl.value)
  } catch (e) {
    emit('capture', { error: e.message })
  }
}

function handleCapture() {
  const b64 = captureFrame(videoEl.value, canvasEl.value)
  if (!b64) return
  flash()
  emit('capture', { b64, mode: activeMode.value, prompt: finalPrompt() })
}

function flash() {
  flashing.value = true
  setTimeout(() => (flashing.value = false), 150)
}

defineExpose({ activeMode })
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <span class="label">📷 Cámara</span>
      <select class="cam-select" v-model="selectedCamera">
        <option v-if="!cameras.length" value="">Sin cámaras</option>
        <option v-for="cam in cameras" :key="cam.deviceId" :value="cam.deviceId">
          {{ cam.label || 'Cámara' }}
        </option>
      </select>
      <button class="btn-icon" @click="loadCameras" title="Actualizar">↺</button>
    </div>

    <div class="video-wrap">
      <video ref="videoEl" autoplay playsinline muted :style="{ display: isActive ? 'block' : 'none' }"></video>
      <canvas ref="canvasEl" style="display:none"></canvas>
      <div class="flash" :class="{ active: flashing }" ref="flashEl"></div>
      <div v-if="!isActive" class="video-placeholder">
        <svg viewBox="0 0 48 48" fill="none">
          <rect x="4" y="10" width="40" height="30" rx="4" stroke="currentColor" stroke-width="2"/>
          <circle cx="24" cy="25" r="8" stroke="currentColor" stroke-width="2"/>
          <circle cx="24" cy="25" r="3" fill="currentColor"/>
          <rect x="17" y="6" width="14" height="6" rx="2" stroke="currentColor" stroke-width="2"/>
        </svg>
        <p>Sin señal</p>
      </div>
    </div>

    <div class="cam-controls">
      <button class="btn-start" @click="handleStart">
        {{ isActive ? '↺ Reiniciar' : '▶ Activar' }}
      </button>
    </div>

    <div class="section-label">Modo de análisis</div>
    <div class="mode-list">
      <button
        v-for="mode in MODES"
        :key="mode.id"
        class="mode-btn"
        :class="{ active: activeMode === mode.id }"
        @click="activeMode = mode.id"
      >{{ mode.label }}</button>
    </div>

    <div class="section-label">Prompt custom</div>
    <textarea
      class="custom-prompt"
      v-model="customPrompt"
      :placeholder="selectedMode().prompt"
      rows="3"
    ></textarea>

    <button class="btn-capture" :disabled="!isActive" @click="handleCapture">
      ⊙ Capturar y analizar
    </button>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  flex-shrink: 0;
  border-right: 1px solid var(--border);
  background: var(--surface);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
}
.sidebar::-webkit-scrollbar { width: 3px; }
.sidebar::-webkit-scrollbar-thumb { background: var(--border-bright); }

.sidebar-header {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.label { font-family: var(--mono); font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; flex: 1; }

.video-wrap {
  position: relative; width: 100%;
  aspect-ratio: 16/9; background: #000; flex-shrink: 0;
}
video { width: 100%; height: 100%; object-fit: cover; display: block; }
.flash {
  position: absolute; inset: 0; background: white;
  opacity: 0; pointer-events: none; transition: opacity 0.1s;
}
.flash.active { opacity: 0.7; }
.video-placeholder {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; color: var(--text-dim);
}
.video-placeholder svg { width: 36px; opacity: 0.3; }
.video-placeholder p { font-family: var(--mono); font-size: 10px; }

.cam-controls { padding: 8px 12px; flex-shrink: 0; }
.btn-start {
  width: 100%; background: var(--surface2);
  border: 1px solid var(--border); color: var(--text-muted);
  font-size: 11px; font-family: var(--mono); padding: 6px;
  border-radius: 6px; cursor: pointer; transition: all 0.15s;
}
.btn-start:hover { border-color: var(--border-bright); color: var(--text); }

.section-label {
  font-family: var(--mono); font-size: 9px; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--text-dim);
  padding: 8px 12px 4px;
}
.mode-list { display: flex; flex-direction: column; gap: 2px; padding: 0 8px; }
.mode-btn {
  text-align: left; padding: 6px 8px; border-radius: 6px;
  font-size: 12px; background: transparent; color: var(--text-muted);
  border: 1px solid transparent; transition: all 0.15s; cursor: pointer;
}
.mode-btn:hover { background: var(--surface2); color: var(--text); }
.mode-btn.active { background: var(--accent-dim); border-color: var(--accent); color: var(--accent); }

.custom-prompt {
  margin: 0 8px; width: calc(100% - 16px);
  background: var(--surface2); border: 1px solid var(--border);
  color: var(--text); font-family: var(--mono); font-size: 11px;
  border-radius: 6px; padding: 8px; resize: none; outline: none;
  transition: border-color 0.2s; line-height: 1.5;
}
.custom-prompt::placeholder { color: var(--text-dim); }
.custom-prompt:focus { border-color: var(--border-bright); }

.btn-capture {
  margin: 10px 8px 12px;
  width: calc(100% - 16px);
  background: var(--accent); color: var(--accent-text);
  font-weight: 700; font-size: 13px; padding: 10px;
  border-radius: 8px; letter-spacing: 0.02em; cursor: pointer;
  transition: all 0.15s; border: none;
}
.btn-capture:hover:not(:disabled) { filter: brightness(1.08); }
.btn-capture:active:not(:disabled) { transform: scale(0.97); }
.btn-capture:disabled { opacity: 0.35; cursor: not-allowed; }

.cam-select {
  background: var(--surface2); border: 1px solid var(--border);
  color: var(--text-muted); font-family: var(--mono); font-size: 10px;
  border-radius: 5px; padding: 3px 6px; outline: none;
  max-width: 90px; overflow: hidden; text-overflow: ellipsis;
}
.btn-icon {
  background: var(--surface2); color: var(--text-muted);
  width: 24px; height: 24px; border-radius: 5px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; border: 1px solid var(--border);
  cursor: pointer; transition: all 0.15s; flex-shrink: 0;
}
.btn-icon:hover { border-color: var(--border-bright); color: var(--text); }
</style>
