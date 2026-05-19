<script setup>
import { ref, computed } from 'vue'
import AppHeader from './components/AppHeader.vue'
import CameraSidebar from './components/CameraSidebar.vue'
import VirtualBoard from './components/VirtualBoard.vue'
import { useAnalysis } from './composables/useAnalysis'

const { isThinking, status, analyze } = useAnalysis()

const cards = ref([])
let cardId = 0

const statusText = computed(() => ({
  offline:  'offline',
  live:     'en vivo',
  thinking: 'analizando...',
  error:    'error',
}[status.value] ?? status.value))

function ts() {
  return new Date().toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

async function onCapture({ b64, mode, prompt, error }) {
  if (error) {
    cards.value.unshift({ id: ++cardId, mode: 'error', content: `⚠ ${error}`, thumbB64: null, time: ts() })
    return
  }

  try {
    const result = await analyze(b64, prompt, mode)
    cards.value.unshift({
      id: ++cardId,
      mode: result.mode,
      content: result.content,
      thumbB64: b64,
      time: ts(),
    })
  } catch (e) {
    cards.value.unshift({ id: ++cardId, mode: 'error', content: `⚠ ${e.message}`, thumbB64: b64, time: ts() })
  }
}

function removeCard(id) {
  cards.value = cards.value.filter(c => c.id !== id)
}

function clearBoard() {
  cards.value = []
}
</script>

<template>
  <AppHeader :status="status" :statusText="statusText">
    <template #actions>
      <button v-if="cards.length" class="btn-clear" @click="clearBoard" title="Limpiar board">
        Limpiar board
      </button>
    </template>
  </AppHeader>

  <div class="workspace">
    <CameraSidebar @capture="onCapture" />
    <VirtualBoard :cards="cards" :isThinking="isThinking" @remove-card="removeCard" />
  </div>
</template>

<style scoped>
.workspace {
  flex: 1;
  display: flex;
  overflow: hidden;
}
.btn-clear {
  background: transparent; border: 1px solid var(--border);
  color: var(--text-muted); font-family: var(--mono); font-size: 10px;
  padding: 4px 10px; border-radius: 6px; cursor: pointer;
  transition: all 0.15s;
}
.btn-clear:hover { border-color: var(--red); color: var(--red); }
</style>
