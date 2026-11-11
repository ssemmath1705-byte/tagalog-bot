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
            "한국어-따갈로그어(Taglish) 전문 통역사로서 카톡에서 보기 좋게 3줄 이내로 핵심만 번역해줘.\n"
            "1. 한국어 입력 시: 자연스러운 따갈로그어 표현과 (한글 발음)\n"
            "2. 따갈로그어/영어 입력 시: 한국어 뜻과 추천 답장 1개(한글 발음 포함)\n"
            f"입력 문장: {user_msg}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 200,
                "temperature": 0.2,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        # 제미나이 AI 호출 (타임아웃을 4.0초로 넉넉하게 잡고 실시간 번역 결과를 가져옵니다)
        res = session.post(url, json=payload, timeout=4.0)
        data = res.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            err_msg = data.get("error", {}).get("message", "응답 오류")
            answer = f"번역 중 오류 발생: {err_msg}"

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
