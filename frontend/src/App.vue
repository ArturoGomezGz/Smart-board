<script setup>
import { ref, computed } from 'vue'
import AppHeader from './components/AppHeader.vue'
import CameraPanel from './components/CameraPanel.vue'
import ResponsePanel from './components/ResponsePanel.vue'
import { useAnalysis } from './composables/useAnalysis'

const { isThinking, status, analyze } = useAnalysis()

const cameraPanel  = ref(null)
const responsePanel = ref(null)

const lastFrameB64 = ref(null)

const statusText = computed(() => ({
  offline:  'offline',
  live:     'en vivo',
  thinking: 'analizando...',
  error:    'error',
}[status.value] ?? status.value))

function onFrameCaptured(b64) {
  lastFrameB64.value = b64
}

function onCameraError(msg) {
  responsePanel.value?.addMessage('system', `⚠ Error de cámara: ${msg}`)
  status.value = 'error'
}

async function onSend({ prompt, auto = false }) {
  const b64 = auto
    ? cameraPanel.value?.captureNow?.() ?? lastFrameB64.value
    : lastFrameB64.value

  if (!b64) {
    if (!auto) responsePanel.value?.addMessage('system', 'Primero captura un frame con el botón ⊙.')
    return
  }

  if (!auto) responsePanel.value?.addMessage('user', prompt, b64)

  try {
    const text = await analyze(b64, prompt)
    responsePanel.value?.addMessage('claude', text)
  } catch (e) {
    responsePanel.value?.addMessage('system', `⚠ ${e.message}`)
  }
}

function onFrameAndSend(b64) {
  lastFrameB64.value = b64
  const rp = responsePanel.value
  if (!rp) return
  const prompt = rp.activePrompt?.() ?? 'Describe todo lo que ves en el pizarrón con detalle.'
  rp.addMessage('user', prompt, b64)
  onSend({ prompt })
}
</script>

<template>
  <AppHeader :status="status" :statusText="statusText" />

  <main>
    <CameraPanel
      ref="cameraPanel"
      @frame-captured="onFrameAndSend"
      @camera-error="onCameraError"
    />
    <ResponsePanel
      ref="responsePanel"
      :isThinking="isThinking"
      @send="onSend"
    />
  </main>
</template>

<style scoped>
main {
  display: grid;
  grid-template-columns: 1fr 340px;
  flex: 1;
  overflow: hidden;
}
</style>
