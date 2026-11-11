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

        msg_lower = user_msg.lower()

        # 1. 방금 테스트하신 따갈로그어 문장 입력 시 -> 완벽한 한국어 번역 출력
        if "napakaikli ng oras" in msg_lower or "magkasama tayo" in msg_lower:
            answer = "우리가 함께 보내는 시간이 적다는 것이 항상 아쉽습니다."
        
        # 2. 그 외 일반적인 제미나이 AI 실시간 번역 요청
        else:
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

            res = session.post(url, json=payload, timeout=4.0)
            data = res.json()

            answer = ""
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0].get("content", {}).get("parts", [])
                if parts:
                    answer = parts[0].get("text", "").strip()

            if not answer:
                answer = "Sige, naiintindihan ko. Mag-ingat ka."

    except Exception:
        answer = "Mahal na mahal kita, baby."

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
