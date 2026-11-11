from fastapi import FastAPI, Request
import requests
import re

app = FastAPI()
session = requests.Session()

GEMINI_API_KEY = "AQ.Ab8RN6JB2PByMqHn-r3MFsfPTWRvjvPBAwKlaCbJLZkKQVPw0g"
ACTIVE_MODEL = "gemini-3.0-flash"

def call_gemini(model_name: str, prompt: str, disable_thinking: bool = True):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    gen_config = {"maxOutputTokens": 300, "temperature": 0.3}
    if disable_thinking:
        gen_config["thinkingConfig"] = {"thinkingBudget": 0}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": gen_config
    }
    return session.post(url, json=payload, timeout=4.2).json()

def translate_with_gemini(user_msg: str) -> str:
    global ACTIVE_MODEL
    prompt = (
        "한국어-따갈로그어(Taglish) 통역사로서 카톡에서 읽기 편하게 4줄 이내로 핵심만 간결하게 답해줘.\n"
        "1. [한국어] 입력 시: 자연스러운 따갈로그어/Taglish 표현 2개와 [한글 발음] 표기\n"
        "2. [따갈로그어/영어] 입력 시: 자연스러운 한국어 뜻과 짧은 추천 답장 1개([한글 발음] 포함)\n"
        f"입력 문장: {user_msg}"
    )
    try:
        for model_name in [ACTIVE_MODEL, "gemini-flash-latest", "gemini-2.5-flash"]:
            data = call_gemini(model_name, prompt, disable_thinking=True)
            if "candidates" in data and len(data["candidates"]) > 0:
                ACTIVE_MODEL = model_name
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            err_msg = data.get("error", {}).get("message", str(data))
            if "thinkingConfig" in err_msg:
                data2 = call_gemini(model_name, prompt, disable_thinking=False)
                if "candidates" in data2 and len(data2["candidates"]) > 0:
                    ACTIVE_MODEL = model_name
                    return data2["candidates"][0]["content"]["parts"][0]["text"].strip()

            match = re.search(r"use models/([a-zA-Z0-9._-]+)", err_msg)
            if match:
                ACTIVE_MODEL = match.group(1)
                retry_data = call_gemini(ACTIVE_MODEL, prompt, disable_thinking=True)
                if "candidates" in retry_data and len(retry_data["candidates"]) > 0:
                    return retry_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return f"API 확인 필요: {err_msg}"
    except Exception as e:
        return f"잠시 후 다시 입력해 주세요. ({str(e)})"

@app.post("/")
@app.post("/translate")
async def kakao_webhook(request: Request):
    try:
        body = await request.json()
        user_msg = body.get("userRequest", {}).get("utterance", "").strip()
        if not user_msg:
            user_msg = "안녕하세요"
        answer = translate_with_gemini(user_msg)
    except Exception as e:
        answer = f"오류 발생: {str(e)}"

    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }

@app.get("/")
@app.get("/translate")
async def root():
    return {"status": "Tagalog Translation Bot is running!"}
