# Smart Board → Claude

Interfaz web que le da "ojos" a Claude apuntando una cámara física a un pizarrón. Captura frames en tiempo real —manual o automático— y los envía a Claude Vision para describir, transcribir, explicar o revisar lo que hay escrito o dibujado.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | Vue 3 + Vite |
| Backend | FastAPI (Python) |
| IA | Claude Vision (`claude-sonnet-4-5`) vía SDK de Anthropic |
| Captura de video | `getUserMedia` / Canvas API |

## Estructura

```
smart-board/
├── backend/
│   ├── main.py             # API: POST /api/analyze, GET /health
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.vue
    │   ├── components/
    │   │   ├── AppHeader.vue
    │   │   ├── CameraPanel.vue
    │   │   └── ResponsePanel.vue
    │   └── composables/
    │       ├── useCamera.js
    │       └── useAnalysis.js
    └── vite.config.js      # proxy /api → localhost:8000
```

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env          # agregar tu ANTHROPIC_API_KEY
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Abrir [http://localhost:5173](http://localhost:5173). El proxy de Vite redirige `/api/*` al backend en el puerto 8000.

## Modos de análisis

| Chip | Acción |
|---|---|
| 👁 Describir | Describe todo lo que hay en el pizarrón |
| 📐 Diagrama | Explica diagramas o esquemas dibujados |
| 📝 Transcribir | Lee y transcribe el texto escrito |
| 💡 Explicar | Explica el concepto o idea principal |
| 🔍 Revisar | Detecta y corrige errores |
| ✏ Custom | Prompt libre |

La auto-captura lanza análisis periódicos con intervalo configurable (mínimo 5 s). Las respuestas de Claude se renderizan en Markdown.

## Flujo de datos

```
Cámara → getUserMedia() → <video>
  └── Canvas.drawImage() → JPEG base64
        └── POST /api/analyze  (FastAPI)
              └── Anthropic SDK → claude-sonnet-4-5
                    └── Respuesta Markdown → UI Vue
```

## Variables de entorno

```bash
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...
```

El `.env` está en `.gitignore` — nunca se sube al repositorio.
