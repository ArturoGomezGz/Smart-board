from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import base64

load_dotenv()

app = FastAPI(title="Smart Board API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class AnalyzeRequest(BaseModel):
    image_b64: str
    prompt: str
    model: str = "claude-sonnet-4-5"
    max_tokens: int = 1000


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    try:
        message = client.messages.create(
            model=req.model,
            max_tokens=req.max_tokens,
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
        return {"text": message.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
