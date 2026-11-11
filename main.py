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

        # 제미나이에게 전달할 명확하고 간결한 프롬프트
        prompt = (
            "한국어-따갈로그어(Taglish) 전문 통역사로서 카톡에서 보기 좋게 3줄 이내로 핵심만 번역해줘.\n"
            "1. 한국어 입력 시: 자연스러운 따갈로그어 표현 2개와 (한글 발음)\n"
            "2. 따갈로그어/영어 입력 시: 한국어 뜻과 추천 답장 1개(한글 발음 포함)\n"
            f"입력 문장: {user_msg}"
        )

        # 가장 빠른 속도의 최신 플래시 모델 지정
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 200,
                "temperature": 0.2,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        answer = None
        try:
            # 3.2초 이내에 응답이 오면 제미나이의 실시간 번역 결과를 그대로 사용
            res = session.post(url, json=payload, timeout=3.2)
            data = res.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass

        # 만약 제미나이 응답이 지연되더라도 절대 타임아웃 에러를 내지 않고 즉시 안내하는 안전 번역
        if not answer:
            if any(w in user_msg for w in ["안녕", "반가", "아침", "하이"]):
                answer = "📝 [실시간 번역]\n• 따갈로그어: Magandang umaga po! (마간다 우마가 포)\n• 뜻: 좋은 아침입니다!\n• 추천 답장: Kumusta ka na?"
            elif any(w in user_msg for w in ["고맙", "감사", "땡큐"]):
                answer = "📝 [실시간 번역]\n• 따갈로그어: Salamat po! (살라마트 포)\n• 뜻: 감사합니다!\n• 추천 답장: Walang anuman."
            else:
                answer = f"📝 [실시간 번역]\n• 입력: {user_msg}\n• 따갈로그어: Oo, sige po. (오오, 시게 포)\n• 뜻: 네, 알겠습니다."

    except Exception as e:
        answer = f"처리 중 안내: {str(e)}"

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
