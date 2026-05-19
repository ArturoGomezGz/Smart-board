<script setup>
defineProps({
  status: { type: String, default: 'offline' },
  statusText: { type: String, default: 'offline' },
})
</script>

<template>
  <header>
    <div class="logo-mark">
      <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="8" cy="8" r="3" fill="#0d0d0f"/>
        <circle cx="8" cy="8" r="6" stroke="#0d0d0f" stroke-width="1.5"/>
        <path d="M8 2V1M8 15v-1M2 8H1m14 0h-1" stroke="#0d0d0f" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </div>
    <h1>Pizarrón <span>→</span> Claude</h1>
    <div class="status-dot">
      <div class="dot" :class="status"></div>
      <span>{{ statusText }}</span>
    </div>
  </header>
</template>

<style scoped>
header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.logo-mark {
  width: 28px; height: 28px;
  background: var(--accent);
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
}
.logo-mark svg { width: 16px; height: 16px; }
h1 { font-size: 15px; font-weight: 700; letter-spacing: 0.04em; }
h1 span { color: var(--text-muted); font-weight: 400; }
.status-dot {
  margin-left: auto;
  display: flex; align-items: center; gap: 6px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-muted);
}
.dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--text-dim);
  transition: background 0.3s;
}
.dot.live { background: var(--accent); box-shadow: 0 0 6px var(--accent); }
.dot.thinking { background: var(--blue); animation: pulse 1s infinite; }
.dot.error { background: var(--red); }
</style>
