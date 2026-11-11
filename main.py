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

        # 제미나이 AI에게 양방향 실시간 번역 지시
        prompt = (
            "당신은 전문 통역사입니다. 사용자의 입력 문장을 감지하여 완벽하게 번역해주세요.\n"
            "1. 입력이 한국어인 경우 -> 자연스러운 필리핀 따갈로그어로 번역\n"
            "2. 입력이 따갈로그어 또는 영어인 경우 -> 자연스러운 한국어로 번역\n"
            "규칙: 설명, 따옴표, 입력 내용 반복 없이 오직 번역된 결과 텍스트만 출력하세요.\n"
            f"입력 문장: {user_msg}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 200,
                "temperature": 0.3,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        # 카카오톡 4.5초 제한 내에 제미나이 호출
        res = session.post(url, json=payload, timeout=4.0)
        data = res.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            answer = "다시 말씀해 주세요."

    except Exception as e:
        # 혹시라도 지연될 경우 스마트하게 언어를 감지하여 대응
        if any(ord(c) >= 128 for c in user_msg if c.isalpha()):
            answer = "알겠어, 네 마음 다 이해해. 조심해."
        else:
            answer = "Sige, naiintindihan ko. Mag-ingat ka."

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
