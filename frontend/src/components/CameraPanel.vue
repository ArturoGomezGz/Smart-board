<script setup>
import { ref, onMounted } from 'vue'
import { useCamera } from '../composables/useCamera'

const emit = defineEmits(['frame-captured', 'camera-error'])

const { cameras, selectedCamera, isActive, loadCameras, startCamera, captureFrame } = useCamera()

const videoEl = ref(null)
const canvasEl = ref(null)
const flashEl = ref(null)
const flashing = ref(false)

onMounted(loadCameras)

async function handleStartCamera() {
  try {
    await startCamera(videoEl.value)
  } catch (e) {
    emit('camera-error', e.message)
  }
}

function capture() {
  const b64 = captureFrame(videoEl.value, canvasEl.value)
  if (!b64) return
  flash()
  emit('frame-captured', b64)
}

function flash() {
  flashing.value = true
  setTimeout(() => (flashing.value = false), 150)
}

defineExpose({ capture })
</script>

<template>
  <div class="camera-panel">
    <div class="camera-toolbar">
      <span class="cam-label">📷 Cámara</span>
      <select class="cam-select" v-model="selectedCamera">
        <option v-if="!cameras.length" value="">Sin cámaras</option>
        <option v-for="cam in cameras" :key="cam.deviceId" :value="cam.deviceId">
          {{ cam.label || `Cámara` }}
        </option>
      </select>
      <button class="btn-icon" @click="loadCameras" title="Actualizar cámaras">↺</button>
      <button class="btn-ghost" @click="handleStartCamera">
        {{ isActive ? 'Reiniciar' : 'Activar' }}
      </button>
    </div>

    <div class="camera-container">
      <video ref="videoEl" autoplay playsinline muted :style="{ display: isActive ? 'block' : 'none' }"></video>
      <canvas ref="canvasEl" style="display:none"></canvas>
      <div class="flash-overlay" :class="{ flash: flashing }" ref="flashEl"></div>

      <div v-if="!isActive" class="camera-placeholder">
        <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="4" y="10" width="40" height="30" rx="4" stroke="currentColor" stroke-width="2"/>
          <circle cx="24" cy="25" r="8" stroke="currentColor" stroke-width="2"/>
          <circle cx="24" cy="25" r="3" fill="currentColor"/>
          <rect x="17" y="6" width="14" height="6" rx="2" stroke="currentColor" stroke-width="2"/>
          <circle cx="38" cy="15" r="2" fill="currentColor"/>
        </svg>
        <p>Activa la cámara para comenzar</p>
      </div>

      <div v-if="isActive" class="capture-overlay">
        <button class="btn-primary" @click="capture">⊙ Capturar y analizar</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.camera-panel {
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border);
  overflow: hidden;
}
.camera-toolbar {
  padding: 10px 14px;
  display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}
.cam-label {
  font-family: var(--mono); font-size: 10px;
  color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.1em; flex: 1;
}
.camera-container {
  flex: 1; position: relative; background: #000;
  overflow: hidden; display: flex;
  align-items: center; justify-content: center;
}
video { width: 100%; height: 100%; object-fit: contain; }
.flash-overlay {
  position: absolute; inset: 0; background: white;
  opacity: 0; pointer-events: none; transition: opacity 0.1s;
}
.flash-overlay.flash { opacity: 0.7; }
.camera-placeholder {
  display: flex; flex-direction: column;
  align-items: center; gap: 16px; color: var(--text-dim);
}
.camera-placeholder svg { width: 48px; height: 48px; opacity: 0.4; }
.camera-placeholder p { font-size: 13px; font-family: var(--mono); }
.capture-overlay {
  position: absolute; bottom: 16px; left: 50%;
  transform: translateX(-50%);
}
.cam-select {
  background: var(--surface2); border: 1px solid var(--border);
  color: var(--text-muted); font-family: var(--mono); font-size: 10px;
  border-radius: 6px; padding: 4px 8px; outline: none; cursor: pointer;
}
.btn-ghost {
  background: transparent; color: var(--text-muted); font-size: 12px;
  padding: 7px 12px; border-radius: 7px; border: 1px solid var(--border);
}
.btn-ghost:hover:not(:disabled) { border-color: var(--border-bright); color: var(--text); }
.btn-icon {
  background: var(--surface2); color: var(--text);
  width: 30px; height: 30px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; border: 1px solid var(--border);
}
.btn-icon:hover:not(:disabled) { border-color: var(--border-bright); }
.btn-primary {
  background: var(--accent); color: var(--accent-text);
  font-weight: 700; font-size: 13px; padding: 8px 16px;
  border-radius: 8px; letter-spacing: 0.03em;
}
.btn-primary:hover:not(:disabled) { filter: brightness(1.08); }
.btn-primary:active:not(:disabled) { transform: scale(0.97); }
</style>
