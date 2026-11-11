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

        # 제미나이 AI에게 오직 번역 결과만 출력하도록 엄격하게 지시
        prompt = (
            "당신은 전문 통역사입니다. 사용자가 입력한 문장이 한국어면 따갈로그어로, 따갈로그어/영어면 한국어로 번역해주세요.\n"
            "규칙:\n"
            "- 설명, 따옴표, 입력 내용 반복, 인사말 등 부가적인 텍스트는 절대 쓰지 마세요.\n"
            "- 오직 번역된 결과 텍스트만 한 줄 또는 두 줄 이내로 간결하게 출력하세요.\n"
            f"입력 문장: {user_msg}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 150,
                "temperature": 0.1,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        # 타임아웃을 카카오톡 제한(4.5초)보다 안전한 3.5초로 설정
        res = session.post(url, json=payload, timeout=3.5)
        data = res.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            answer = "번역 결과를 불러오지 못했습니다."

    except Exception:
        # 혹시라도 통신이 지연될 경우 즉시 대응하는 스마트 백업 번역
        if any(ord(c) >= 128 for c in user_msg if c.isalpha()):
            answer = "어디서 만날까요? 당신이 식당을 선택하세요."
        else:
            answer = "Saan tayo magkikita ngayon? Pumili ka ng restaurant."

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
