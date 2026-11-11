from fastapi import FastAPI, Request
import requests

app = FastAPI()
session = requests.Session()

GEMINI_API_KEY = "AQ.Ab8RN6JB2PByMqHn-r3MFsfPTWRvjvPBAwKlaCbJLZkKQVPw0g"

@app.post("/")
@app.post("/translate")
async def kakao_webhook(request: Request):
    try:
        body = await request.json()
        user_msg = body.get("userRequest", {}).get("utterance", "").strip()
        if not user_msg:
            user_msg = "안녕하세요"

        prompt = (
            "너는 한국어와 필리핀 따갈로그어(Taglish 포함) 전문 통역사야.\n"
            "카카오톡에서 읽기 편하게 3줄 이내로 간결하게 답해줘.\n"
            "1. 한국어 입력 시: 자연스러운 따갈로그어 표현 2개와 (한글 발음)\n"
            "2. 따갈로그어/영어 입력 시: 자연스러운 한국어 뜻과 센스 있는 추천 답장 1개(한글 발음 포함)\n"
            f"입력 문장: {user_msg}"
        )

        # 가장 빠르고 안정적인 모델로 바로 요청
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 250, 
                "temperature": 0.3,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        res = session.post(url, json=payload, timeout=4.2)
        data = res.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            err_msg = data.get("error", {}).get("message", "AI 응답 확인 필요")
            answer = f"번역 처리 중 문제가 발생했습니다: {err_msg}"

    except Exception as e:
        answer = f"통신 지연 또는 오류: {str(e)}"

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
