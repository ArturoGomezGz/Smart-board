import { ref } from 'vue'

const API_URL = '/api/analyze'

export function useAnalysis() {
  const isThinking = ref(false)
  const status = ref('offline')

  async function analyze(imageB64, prompt) {
    if (isThinking.value) return null
    isThinking.value = true
    status.value = 'thinking'

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_b64: imageB64, prompt }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Error del servidor')
      status.value = 'live'
      return data.text
    } catch (e) {
      status.value = 'error'
      throw e
    } finally {
      isThinking.value = false
    }
  }

  return { isThinking, status, analyze }
}
