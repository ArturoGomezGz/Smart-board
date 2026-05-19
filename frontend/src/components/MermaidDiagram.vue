<script setup>
import { ref, onMounted, watch } from 'vue'
import mermaid from 'mermaid'

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    darkMode: true,
    background: '#1e1e24',
    primaryColor: '#b8ff57',
    primaryTextColor: '#e8e8ec',
    primaryBorderColor: 'rgba(255,255,255,0.18)',
    lineColor: '#666680',
    secondaryColor: '#16161a',
    tertiaryColor: '#1e1e24',
    fontSize: '13px',
  },
})

const props = defineProps({ code: { type: String, required: true } })

const container = ref(null)
const error = ref(null)
let uid = 0

async function render() {
  error.value = null
  if (!container.value || !props.code.trim()) return
  try {
    const id = `mermaid-${++uid}`
    const { svg } = await mermaid.render(id, props.code.trim())
    container.value.innerHTML = svg
  } catch (e) {
    error.value = 'No se pudo renderizar el diagrama.'
  }
}

onMounted(render)
watch(() => props.code, render)
</script>

<template>
  <div class="mermaid-wrap">
    <div v-if="error" class="mermaid-error">{{ error }}</div>
    <div v-else ref="container" class="mermaid-container"></div>
  </div>
</template>

<style scoped>
.mermaid-wrap { width: 100%; }
.mermaid-container { width: 100%; overflow-x: auto; }
.mermaid-container :deep(svg) { max-width: 100%; height: auto; }
.mermaid-error {
  font-family: var(--mono); font-size: 11px;
  color: var(--red); padding: 8px;
  background: rgba(255,87,87,0.08); border-radius: 6px;
}
</style>
