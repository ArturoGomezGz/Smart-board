<script setup>
import BoardCard from './BoardCard.vue'

const props = defineProps({
  cards: { type: Array, default: () => [] },
  isThinking: Boolean,
})

const emit = defineEmits(['remove-card'])
</script>

<template>
  <div class="board">
    <div v-if="!cards.length && !isThinking" class="empty-board">
      <div class="empty-icon">⬡</div>
      <p>El board está vacío</p>
      <p class="sub">Captura algo del pizarrón para comenzar</p>
    </div>

    <div v-if="isThinking" class="thinking-card">
      <span class="thinking-badge">Analizando</span>
      <div class="thinking-dots">
        <span>•</span><span>•</span><span>•</span>
      </div>
    </div>

    <BoardCard
      v-for="card in cards"
      :key="card.id"
      :card="card"
      @remove="emit('remove-card', $event)"
    />
  </div>
</template>

<style scoped>
.board {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.board::-webkit-scrollbar { width: 4px; }
.board::-webkit-scrollbar-track { background: transparent; }
.board::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 2px; }

.empty-board {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 8px;
  color: var(--text-dim);
}
.empty-icon { font-size: 48px; opacity: 0.2; line-height: 1; }
.empty-board p { font-size: 14px; font-weight: 600; }
.empty-board .sub { font-family: var(--mono); font-size: 11px; color: var(--text-dim); }

.thinking-card {
  background: var(--surface);
  border: 1px solid var(--accent);
  border-radius: var(--radius);
  padding: 20px 24px;
  display: flex; align-items: center; gap: 12px;
  animation: slideIn 0.2s ease-out;
}
.thinking-badge {
  font-family: var(--mono); font-size: 10px; font-weight: 700;
  color: var(--accent); letter-spacing: 0.08em; text-transform: uppercase;
}
.thinking-dots span {
  animation: blink 1.2s infinite; color: var(--accent); font-size: 18px;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
</style>
