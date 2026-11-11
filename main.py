from fastapi import FastAPI, Request
import requests
import re

app = FastAPI()

GEMINI_API_KEY = "AQ.Ab8RN6JB2PByMqHn-r3MFsfPTWRvjvPBAwKlaCbJLZkKQVPw0g"

def call_gemini(model_name: str, prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    return requests.post(url, json=payload, timeout=4.5).json()

def translate_with_gemini(user_msg: str) -> str:
    prompt = (
        "너는 한국어와 필리핀 따갈로그어(Taglish 및 현지 줄임말 포함) 전문 통역 챗봇이야.\n"
        "1. 입력된 문장이 [한국어]라면:\n"
        "- 자연스러운 일상 따갈로그어와 현지인이 자주 쓰는 Taglish 표현 2가지를 알려줘.\n"
        "- 바로 밑에 한글 발음을 적어줘.\n\n"
        "2. 입력된 문장이 [따갈로그어/영어/Taglish]라면:\n"
        "- 자연스러운 한국어로 번역해줘.\n"
        "- 줄임말이나 핵심 단어가 있다면 간단히 뜻을 풀이해줘.\n"
        "- 이어서 답장하기 좋은 센스 있는 따갈로그어 답변 1개(한글 발음 포함)를 추천해줘.\n\n"
        "불필요한 인사말 없이 카톡에서 읽기 편하게 간결하게 답변해.\n\n"
        f"입력 문장: {user_msg}"
    )
    try:
        models_to_try = ["gemini-3.8-flash", "gemini-3.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]
        last_err = ""
        for model_name in models_to_try:
            data = call_gemini(model_name, prompt)
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            last_err = data.get("error", {}).get("message", str(data))
            match = re.search(r"use models/([a-zA-Z0-9._-]+)", last_err)
            if match:
                rec_model = match.group(1)
                retry_data = call_gemini(rec_model, prompt)
                if "candidates" in retry_data and len(retry_data["candidates"]) > 0:
                    return retry_data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return f"API 확인 필요: {last_err}"
    except Exception as e:
        return f"통신 지연 또는 오류: {str(e)}"

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
