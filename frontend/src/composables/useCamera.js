import { ref } from 'vue'

export function useCamera() {
  const stream = ref(null)
  const cameras = ref([])
  const selectedCamera = ref('')
  const isActive = ref(false)

  async function loadCameras() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      cameras.value = devices.filter(d => d.kind === 'videoinput')
      if (cameras.value.length && !selectedCamera.value) {
        selectedCamera.value = cameras.value[0].deviceId
      }
    } catch {
      cameras.value = []
    }
  }

  async function startCamera(videoEl) {
    if (stream.value) {
      stream.value.getTracks().forEach(t => t.stop())
    }
    const constraints = {
      video: selectedCamera.value
        ? { deviceId: { exact: selectedCamera.value }, width: { ideal: 1280 }, height: { ideal: 720 } }
        : { width: { ideal: 1280 }, height: { ideal: 720 } },
    }
    stream.value = await navigator.mediaDevices.getUserMedia(constraints)
    videoEl.srcObject = stream.value
    isActive.value = true
    await loadCameras()
  }

  function captureFrame(videoEl, canvasEl) {
    if (!stream.value) return null
    const vw = videoEl.videoWidth
    const vh = videoEl.videoHeight
    if (!vw || !vh) return null
    canvasEl.width = vw
    canvasEl.height = vh
    canvasEl.getContext('2d').drawImage(videoEl, 0, 0, vw, vh)
    return canvasEl.toDataURL('image/jpeg', 0.85).split(',')[1]
  }

  return { stream, cameras, selectedCamera, isActive, loadCameras, startCamera, captureFrame }
}
