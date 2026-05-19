from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Smart Board API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPTS = {
    "diagram": (
        "Eres un experto en diagramas y visualización. "
        "El usuario te enviará una foto de un pizarrón con un diagrama dibujado a mano. "
        "Tu tarea es interpretarlo y devolver ÚNICAMENTE código Mermaid válido que represente ese diagrama de forma limpia y profesional. "
        "No incluyas explicaciones, ni bloques de código markdown (```), solo el código Mermaid puro. "
        "Si no puedes identificar un diagrama claro, genera un flowchart con los elementos que veas."
    ),
    "transcribe": (
        "Eres un asistente de transcripción preciso. "
        "Lee todo el texto que aparece en el pizarrón y transcríbelo en Markdown limpio y bien estructurado. "
        "Usa encabezados, listas y énfasis donde corresponda. "
        "Conserva la estructura y jerarquía del contenido original."
    ),
    "explain": (
        "Eres un profesor experto. "
        "Observa el contenido del pizarrón y genera una explicación clara y estructurada en Markdown. "
        "Incluye: concepto principal, puntos clave, y contexto relevante. "
        "Usa encabezados, listas y ejemplos cuando sea útil."
    ),
    "review": (
        "Eres un revisor experto. "
        "Analiza el contenido del pizarrón e identifica errores (ortografía, lógica, matemáticas, sintaxis, etc.). "
        "Devuelve un reporte en Markdown con: versión corregida y lista de correcciones con explicación breve."
    ),
    "code": (
        "Eres un desarrollador senior. "
        "Observa el pseudocódigo, arquitectura o diagrama de código en el pizarrón y genera el código real equivalente. "
        "Devuelve Markdown con el bloque de código en el lenguaje más apropiado según lo que veas. "
        "Si hay arquitectura, genera la estructura de archivos y los archivos principales."
    ),
    "describe": (
        "Describe detalladamente todo lo que ves en el pizarrón. "
        "Sé específico con el contenido, estructura y cualquier detalle relevante. "
        "Responde en Markdown bien formateado."
    ),
}


class AnalyzeRequest(BaseModel):
    image_b64: str
    prompt: str
    mode: str = "describe"
    model: str = "claude-sonnet-4-5"
    max_tokens: int = 2000


class AnalyzeResponse(BaseModel):
    content: str
    mode: str


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    system = SYSTEM_PROMPTS.get(req.mode, SYSTEM_PROMPTS["describe"])
    try:
        message = client.messages.create(
            model=req.model,
            max_tokens=req.max_tokens,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": req.image_b64,
                            },
                        },
                        {"type": "text", "text": req.prompt},
                    ],
                }
            ],
        )
        return AnalyzeResponse(content=message.content[0].text, mode=req.mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
