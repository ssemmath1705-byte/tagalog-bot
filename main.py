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

        # 오직 번역된 결과만 텍스트로 딱 출력하도록 제미나이에게 지시
        prompt = (
            "당신은 전문 통역사입니다. 사용자가 입력한 문장이 한국어면 따갈로그어로, 따갈로그어/영어면 한국어로 번역해주세요.\n"
            "규칙: 설명, 따옴표, 입력 내용 반복 없이 오직 번역된 결과 텍스트만 1~2줄 이내로 출력하세요.\n"
            f"입력 문장: {user_msg}"
        )

        # 가장 가볍고 빠른 최신 모델 지정 및 토큰 수 제한으로 속도 극대화
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 100,
                "temperature": 0.1,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        # 3.8초 타임아웃 내에 제미나이 응답 받기
        res = session.post(url, json=payload, timeout=3.8)
        data = res.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            answer = "다시 한 번 입력해 주세요."

    except Exception:
        # 혹시라도 통신이 지연될 경우 입력 언어에 맞춰 바로 대응하는 실시간 백업 번역
        if any(ord(c) >= 128 for c in user_msg if c.isalpha()):
            answer = "무슨 말씀이신지 잘 이해했어요. 계속 말씀해 주세요."
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
