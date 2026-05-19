<script setup>
import { ref, watch, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ breaks: true })

function renderMd(text) {
  return DOMPurify.sanitize(marked.parse(text))
}

const MODES = [
  { label: '👁 Describir',   prompt: 'Describe todo lo que ves en el pizarrón con detalle.' },
  { label: '📐 Diagrama',    prompt: '¿Qué diagrama o esquema hay dibujado? Explícalo.' },
  { label: '📝 Transcribir', prompt: 'Lee y transcribe todo el texto escrito en el pizarrón.' },
  { label: '💡 Explicar',    prompt: 'Explica el concepto o idea principal que se muestra en el pizarrón.' },
  { label: '🔍 Revisar',     prompt: '¿Hay errores en lo que está escrito en el pizarrón? Corrígelos.' },
  { label: '✏ Custom',      prompt: '' },
]

defineProps({ isThinking: Boolean })
const emit = defineEmits(['send'])

const messages  = ref([])
const activeMode = ref(0)
const customPrompt = ref('')
const messagesEl = ref(null)
const autoCapture = ref(false)
const intervalSecs = ref(15)

let autoInterval = null

const activePrompt = () => customPrompt.value.trim() || MODES[activeMode.value].prompt

function selectMode(i) {
  activeMode.value = i
  if (MODES[i].prompt) customPrompt.value = ''
}

function ts() {
  return new Date().toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function addMessage(role, text, thumbB64 = null) {
  messages.value.push({ role, text, thumbB64, time: ts() })
  nextTick(() => {
    if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  })
}

function clear() {
  messages.value = []
}

function handleSend() {
  const prompt = activePrompt()
  if (!prompt) return
  emit('send', { prompt })
}

function toggleAuto(enabled) {
  if (autoInterval) { clearInterval(autoInterval); autoInterval = null }
  if (enabled) {
    autoInterval = setInterval(() => {
      emit('send', { prompt: activePrompt(), auto: true })
    }, (parseInt(intervalSecs.value) || 15) * 1000)
  }
}

watch(autoCapture, toggleAuto)
watch(intervalSecs, () => { if (autoCapture.value) toggleAuto(true) })

defineExpose({ addMessage, clear, activePrompt })
</script>

<template>
  <div class="response-panel">
    <div class="panel-header">
      <span class="panel-title">💬 Respuesta de Claude</span>
      <button class="btn-icon" @click="clear" title="Limpiar">✕</button>
    </div>

    <div class="mode-chips">
      <button
        v-for="(mode, i) in MODES"
        :key="i"
        class="chip"
        :class="{ active: activeMode === i }"
        @click="selectMode(i)"
      >{{ mode.label }}</button>
    </div>

    <div class="auto-row">
      <span class="toggle-label">Auto-captura</span>
      <label class="toggle">
        <input type="checkbox" v-model="autoCapture" />
        <span class="slider-tog"></span>
      </label>
      <span class="toggle-label">cada</span>
      <input class="interval-input" type="number" v-model="intervalSecs" min="5" max="300" />
      <span class="toggle-label">seg</span>
    </div>

    <div class="messages-container" ref="messagesEl">
      <div v-if="!messages.length" class="empty-state">
        <p>Apunta la cámara al pizarrón,<br>actívala y captura un frame.<br><br>Claude lo analizará al instante.</p>
      </div>

      <div v-for="(msg, i) in messages" :key="i" class="message">
        <div class="message-meta">
          <span class="message-role" :class="msg.role">
            {{ msg.role === 'claude' ? 'Claude' : msg.role === 'user' ? 'Tú' : 'Sistema' }}
          </span>
          <span class="message-ts">{{ msg.time }}</span>
        </div>
        <div v-if="msg.thumbB64" class="message-thumb">
          <img :src="`data:image/jpeg;base64,${msg.thumbB64}`" alt="Frame capturado" />
        </div>
        <div
          class="message-bubble"
          :class="msg.role"
          v-if="msg.role === 'claude'"
          v-html="renderMd(msg.text)"
        ></div>
        <div
          class="message-bubble"
          :class="msg.role"
          v-else
        >{{ msg.text }}</div>
      </div>

      <div v-if="isThinking" class="message">
        <div class="message-meta">
          <span class="message-role claude">Claude</span>
        </div>
        <div class="message-bubble claude thinking-dots">
          <span>•</span><span>•</span><span>•</span>
        </div>
      </div>
    </div>

    <footer>
      <textarea
        class="prompt-input"
        v-model="customPrompt"
        :placeholder="MODES[activeMode].prompt || 'Escribe tu pregunta...'"
        rows="1"
        @keydown.ctrl.enter="handleSend"
        @keydown.meta.enter="handleSend"
      ></textarea>
      <button class="btn-primary" @click="handleSend" :disabled="isThinking">Enviar ↗</button>
      <span class="shortcut">⌘↵</span>
    </footer>
  </div>
</template>

<style scoped>
.response-panel {
  display: flex; flex-direction: column;
  background: var(--surface); overflow: hidden;
}
.panel-header {
  padding: 10px 14px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.panel-title {
  font-family: var(--mono); font-size: 10px; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.1em; flex: 1;
}
.mode-chips {
  display: flex; gap: 4px; padding: 8px 14px;
  border-bottom: 1px solid var(--border); flex-wrap: wrap; flex-shrink: 0;
}
.chip {
  font-family: var(--mono); font-size: 10px; padding: 3px 8px;
  border-radius: 20px; border: 1px solid var(--border); color: var(--text-muted);
  cursor: pointer; transition: all 0.15s; background: transparent; letter-spacing: 0.03em;
}
.chip.active { background: var(--accent-dim); border-color: var(--accent); color: var(--accent); }
.chip:hover:not(.active) { border-color: var(--border-bright); color: var(--text); }
.auto-row {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 14px; border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.toggle-label { font-family: var(--mono); font-size: 10px; color: var(--text-muted); }
.toggle { position: relative; width: 28px; height: 15px; display: inline-block; }
.toggle input { opacity: 0; width: 0; height: 0; }
.slider-tog {
  position: absolute; inset: 0; background: var(--surface2);
  border: 1px solid var(--border); border-radius: 15px; cursor: pointer; transition: 0.2s;
}
.slider-tog::before {
  content: ''; position: absolute; width: 9px; height: 9px;
  left: 2px; top: 2px; background: var(--text-dim); border-radius: 50%; transition: 0.2s;
}
.toggle input:checked + .slider-tog { background: var(--accent-dim); border-color: var(--accent); }
.toggle input:checked + .slider-tog::before { transform: translateX(13px); background: var(--accent); }
.interval-input {
  background: var(--surface2); border: 1px solid var(--border); color: var(--text-muted);
  font-family: var(--mono); font-size: 10px; border-radius: 5px;
  padding: 2px 6px; width: 44px; outline: none; text-align: center;
}
.messages-container {
  flex: 1; overflow-y: auto; padding: 12px;
  display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth;
}
.messages-container::-webkit-scrollbar { width: 4px; }
.messages-container::-webkit-scrollbar-track { background: transparent; }
.messages-container::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 2px; }
.empty-state {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 8px; color: var(--text-dim); padding: 2rem; text-align: center;
}
.empty-state p { font-size: 12px; font-family: var(--mono); line-height: 1.6; }
.message { display: flex; flex-direction: column; gap: 6px; animation: slideIn 0.2s ease-out; }
.message-meta { display: flex; align-items: center; gap: 6px; }
.message-role {
  font-family: var(--mono); font-size: 10px; font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase;
}
.message-role.claude { color: var(--accent); }
.message-role.user { color: var(--blue); }
.message-ts { font-family: var(--mono); font-size: 9px; color: var(--text-dim); }
.message-bubble {
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 10px 12px;
  font-size: 13px; line-height: 1.65; color: var(--text); white-space: pre-wrap;
}
.message-bubble.claude { border-left: 2px solid var(--accent); }
.message-bubble.user   { border-left: 2px solid var(--blue); }

/* Markdown dentro de burbujas de Claude */
.message-bubble :deep(p)          { margin: 0 0 0.5em; }
.message-bubble :deep(p:last-child) { margin-bottom: 0; }
.message-bubble :deep(h1),
.message-bubble :deep(h2),
.message-bubble :deep(h3)         { font-size: 13px; font-weight: 700; margin: 0.6em 0 0.3em; color: var(--accent); }
.message-bubble :deep(ul),
.message-bubble :deep(ol)         { padding-left: 1.2em; margin: 0.4em 0; }
.message-bubble :deep(li)         { margin: 0.2em 0; }
.message-bubble :deep(code)       { font-family: var(--mono); font-size: 11px; background: var(--bg); padding: 1px 5px; border-radius: 4px; color: var(--accent); }
.message-bubble :deep(pre)        { background: var(--bg); border-radius: 6px; padding: 10px 12px; overflow-x: auto; margin: 0.5em 0; }
.message-bubble :deep(pre code)   { background: none; padding: 0; color: var(--text); }
.message-bubble :deep(strong)     { font-weight: 700; color: var(--text); }
.message-bubble :deep(em)         { font-style: italic; color: var(--text-muted); }
.message-bubble :deep(hr)         { border: none; border-top: 1px solid var(--border); margin: 0.6em 0; }
.message-bubble :deep(blockquote) { border-left: 2px solid var(--border-bright); padding-left: 0.8em; color: var(--text-muted); margin: 0.4em 0; }
.message-thumb { width: 100%; border-radius: 6px; overflow: hidden; border: 1px solid var(--border); }
.message-thumb img { width: 100%; display: block; }
.thinking-dots span { animation: blink 1.2s infinite; color: var(--accent); font-size: 18px; }
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
footer {
  border-top: 1px solid var(--border); padding: 12px 16px;
  display: flex; align-items: center; gap: 10px;
  background: var(--surface); flex-shrink: 0;
}
.prompt-input {
  flex: 1; background: var(--surface2); border: 1px solid var(--border);
  border-radius: 8px; padding: 8px 12px; color: var(--text);
  font-family: var(--sans); font-size: 13px; resize: none;
  height: 38px; outline: none; transition: border-color 0.2s;
}
.prompt-input::placeholder { color: var(--text-dim); }
.prompt-input:focus { border-color: var(--border-bright); }
.btn-primary {
  background: var(--accent); color: var(--accent-text);
  font-weight: 700; font-size: 13px; padding: 8px 16px;
  border-radius: 8px; letter-spacing: 0.03em;
}
.btn-primary:hover:not(:disabled) { filter: brightness(1.08); }
.btn-primary:active:not(:disabled) { transform: scale(0.97); }
.btn-icon {
  background: var(--surface2); color: var(--text); width: 30px; height: 30px;
  border-radius: 6px; display: flex; align-items: center; justify-content: center;
  font-size: 13px; border: 1px solid var(--border);
}
.shortcut {
  font-family: var(--mono); font-size: 9px; color: var(--text-dim);
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 4px; padding: 2px 5px;
}
</style>
