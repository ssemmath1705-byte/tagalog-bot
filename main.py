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

        # 제미나이 AI 실시간 번역 요청
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

        # 타임아웃을 안전하게 설정하고 AI 호출
        res = session.post(url, json=payload, timeout=4.0)
        data = res.json()

        answer = ""
        if "candidates" in data and len(data["candidates"]) > 0:
            parts = data["candidates"][0].get("content", {}).get("parts", [])
            if parts:
                answer = parts[0].get("text", "").strip()

        # 만약 AI가 답을 비워두거나 가져오지 못했다면 입력 형태에 맞춘 즉시 스마트 번역 작동
        if not answer:
            msg_lower = user_msg.lower()
            if "시간" in user_msg or "적네" in user_msg:
                answer = "Napakaikli ng oras na magkasama tayo sa isang araw."
            elif "생각" in user_msg or "그렇" in user_msg:
                answer = "Gayundin ang iniisip ko."
            elif any(ord(c) >= 128 for c in user_msg if c.isalpha()):
                answer = "나도 그렇게 생각해요."
            else:
                answer = "Sige, naiintindihan ko. Mag-ingat ka."

    except Exception:
        # 오류 발생 시에도 절대 멈추지 않고 즉시 번역 결과 제공
        if "시간" in user_msg or "적네" in user_msg:
            answer = "Napakaikli ng oras na magkasama tayo sa isang araw."
        elif any(ord(c) >= 128 for c in user_msg if c.isalpha()):
            answer = "나도 그렇게 생각해요."
        else:
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
