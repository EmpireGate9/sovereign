from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="PAI-6 Sovereign API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

class ChatIn(BaseModel):
    text: str
    lang: Optional[str] = "ar"

@app.get("/api/system/healthz")
def healthz():
    return {"ok": True}

@app.post("/api/chat")
async def chat(body: ChatIn):
    txt = (body.text or "").strip()
    lang = (body.lang or "ar").lower()
    if not txt:
        return {"reply": "اكتب رسالتك أولًا." if lang == "ar" else "Please type a message first."}
    return {"reply": (f"فهمت: «{txt}»" if lang.startswith("ar") else f"I got: “{txt}”")}

@app.post("/api/chat/audio")
async def chat_audio(audio: UploadFile = File(...), lang: str = Form("ar")):
    size = 0
    async for chunk in audio.stream():
        size += len(chunk)
    if lang.lower().startswith("ar"):
        return {"reply": f"تم استلام صوت ({audio.filename}, {round(size/1024,1)}KB)"}
    return {"reply": f"Audio received ({audio.filename}, {round(size/1024,1)}KB)"}
