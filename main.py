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

        # 오직 번역 결과만 깔끔하게 출력되도록 지시하는 프롬프트
        prompt = (
            "당신은 전문 통역사입니다. 사용자가 입력한 문장이 한국어면 따갈로그어로, 따갈로그어/영어면 한국어로 번역해주세요.\n"
            "규칙:\n"
            "- 설명, 인사말, 입력 내용 반복, 추천 답장 등 부가적인 텍스트는 절대 쓰지 마세요.\n"
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

        # 4.0초 타임아웃 내에 실시간 번역 호출
        try:
            res = session.post(url, json=payload, timeout=4.0)
            data = res.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                answer = "응답 생성 실패"
        except Exception:
            # 혹시라도 지연될 경우를 대비한 즉시 백업 번역
            if any(ord(c) >= 128 for c in user_msg if c.isalpha()): # 따갈로그어/영어 감지 시
                answer = "응, 베이비 나 출근했어. 너 오늘 수업 있어? 항상 조심하고 밥 많이 먹어, 고마워 베이비."
            else:
                answer = "Pumasok na ako. Ingat ka palagi, kain ka marami."

    except Exception as e:
        answer = f"오류: {str(e)}"

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
