<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import MermaidDiagram from './MermaidDiagram.vue'

marked.setOptions({ breaks: true })

const props = defineProps({
  card: { type: Object, required: true },
})

const emit = defineEmits(['remove'])

const MODE_META = {
  diagram:   { label: '📐 Diagrama',    color: '#b8ff57' },
  transcribe:{ label: '📝 Transcripción', color: '#57b8ff' },
  explain:   { label: '💡 Explicación',  color: '#ffb857' },
  review:    { label: '🔍 Revisión',     color: '#ff57b8' },
  code:      { label: '💻 Código',       color: '#b857ff' },
  describe:  { label: '👁 Descripción',  color: '#57ffb8' },
}

const meta = computed(() => MODE_META[props.card.mode] ?? MODE_META.describe)
const renderedMd = computed(() => DOMPurify.sanitize(marked.parse(props.card.content)))

const thumbExpanded = ref(false)

function copyContent() {
  navigator.clipboard.writeText(props.card.content)
}

function downloadMd() {
  const blob = new Blob([props.card.content], { type: 'text/markdown' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `smartboard-${props.card.mode}-${Date.now()}.md`
  a.click()
}

function downloadSvg() {
  const svg = document.querySelector(`#card-${props.card.id} svg`)
  if (!svg) return
  const blob = new Blob([svg.outerHTML], { type: 'image/svg+xml' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `smartboard-diagram-${Date.now()}.svg`
  a.click()
}
</script>

<template>
  <div class="card" :id="`card-${card.id}`">
    <div class="card-header">
      <span class="card-badge" :style="{ color: meta.color, borderColor: meta.color + '40', background: meta.color + '12' }">
        {{ meta.label }}
      </span>
      <span class="card-ts">{{ card.time }}</span>
      <div class="card-actions">
        <button class="action-btn" @click="copyContent" title="Copiar">⎘</button>
        <button v-if="card.mode === 'diagram'" class="action-btn" @click="downloadSvg" title="Exportar SVG">↓ SVG</button>
        <button v-else class="action-btn" @click="downloadMd" title="Exportar Markdown">↓ MD</button>
        <button class="action-btn danger" @click="emit('remove', card.id)" title="Eliminar">✕</button>
      </div>
    </div>

    <div class="card-body">
      <div class="thumb-col">
        <img
          :src="`data:image/jpeg;base64,${card.thumbB64}`"
          alt="Captura"
          class="thumb"
          :class="{ expanded: thumbExpanded }"
          @click="thumbExpanded = !thumbExpanded"
        />
        <span class="thumb-hint">{{ thumbExpanded ? 'Clic para reducir' : 'Clic para ampliar' }}</span>
      </div>

      <div class="output-col">
        <MermaidDiagram v-if="card.mode === 'diagram'" :code="card.content" />
        <div v-else class="md-output" v-html="renderedMd"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  animation: slideIn 0.25s ease-out;
}
.card-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--surface2);
}
.card-badge {
  font-family: var(--mono); font-size: 10px; font-weight: 700;
  padding: 2px 8px; border-radius: 20px; border: 1px solid;
  letter-spacing: 0.05em;
}
.card-ts {
  font-family: var(--mono); font-size: 10px; color: var(--text-dim);
}
.card-actions {
  margin-left: auto; display: flex; gap: 4px;
}
.action-btn {
  background: var(--bg); border: 1px solid var(--border);
  color: var(--text-muted); font-family: var(--mono);
  font-size: 10px; padding: 3px 8px; border-radius: 5px;
  cursor: pointer; transition: all 0.15s;
}
.action-btn:hover { border-color: var(--border-bright); color: var(--text); }
.action-btn.danger:hover { border-color: var(--red); color: var(--red); }
.card-body {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 0;
  min-height: 180px;
}
.thumb-col {
  border-right: 1px solid var(--border);
  padding: 12px;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  background: #000;
}
.thumb {
  width: 100%; border-radius: 4px; cursor: pointer;
  transition: all 0.2s; object-fit: contain;
}
.thumb.expanded { position: fixed; inset: 10%; z-index: 100; width: auto; max-height: 80vh; border-radius: 8px; box-shadow: 0 0 0 100vw rgba(0,0,0,0.8); }
.thumb-hint { font-family: var(--mono); font-size: 9px; color: var(--text-dim); }
.output-col { padding: 16px; overflow: auto; }
.md-output {
  font-size: 13px; line-height: 1.7; color: var(--text);
}
.md-output :deep(p)            { margin: 0 0 0.6em; }
.md-output :deep(p:last-child) { margin-bottom: 0; }
.md-output :deep(h1),
.md-output :deep(h2),
.md-output :deep(h3)           { font-weight: 700; margin: 0.8em 0 0.3em; color: var(--accent); }
.md-output :deep(h1)           { font-size: 15px; }
.md-output :deep(h2)           { font-size: 14px; }
.md-output :deep(h3)           { font-size: 13px; }
.md-output :deep(ul),
.md-output :deep(ol)           { padding-left: 1.3em; margin: 0.4em 0; }
.md-output :deep(li)           { margin: 0.25em 0; }
.md-output :deep(code)         { font-family: var(--mono); font-size: 11px; background: var(--bg); padding: 1px 5px; border-radius: 4px; color: var(--accent); }
.md-output :deep(pre)          { background: var(--bg); border-radius: 6px; padding: 12px; overflow-x: auto; margin: 0.6em 0; border: 1px solid var(--border); }
.md-output :deep(pre code)     { background: none; padding: 0; color: var(--text); }
.md-output :deep(strong)       { font-weight: 700; color: var(--text); }
.md-output :deep(em)           { color: var(--text-muted); }
.md-output :deep(blockquote)   { border-left: 2px solid var(--border-bright); padding-left: 0.8em; color: var(--text-muted); margin: 0.5em 0; }
.md-output :deep(hr)           { border: none; border-top: 1px solid var(--border); margin: 0.8em 0; }
</style>
