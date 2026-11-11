from fastapi import FastAPI, Request
import requests
import threading

app = FastAPI()
session = requests.Session()

GEMINI_API_KEY = "AQ.Ab8RN6JB2PByMqHn-r3MFsfPTWRvjvPBAwKlaCbJLZkKQVPw0g"

# 직전 번역 결과를 임시로 저장하는 공간
LAST_RESULT = {}

def fetch_gemini(user_msg: str):
    try:
        prompt = (
            "한국어-따갈로그어(Taglish) 통역사로서 카톡에서 보기 좋게 3줄 이내로 핵심만 번역해줘.\n"
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
        res = session.post(url, json=payload, timeout=15.0)
        data = res.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            ans = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            LAST_RESULT["text"] = f"📝 [실시간 번역 결과]\n\n{ans}"
    except Exception:
        pass

@app.post("/")
@app.post("/translate")
async def kakao_webhook(request: Request):
    try:
        body = await request.json()
        user_msg = body.get("userRequest", {}).get("utterance", "").strip()
        if not user_msg:
            user_msg = "안녕하세요"

        # 사용자가 번역 결과 확인차 '1'이나 '.'을 입력한 경우
        if user_msg in ["1", ".", "결과"]:
            answer = LAST_RESULT.get("text", "아직 완료된 번역이 없습니다. 문장을 먼저 입력해 주세요.")
        else:
            # 먼저 0.1초 만에 카카오톡 타임아웃을 방지하는 응답을 보내고, 백그라운드에서 제미나이를 호출합니다.
            LAST_RESULT["text"] = "⏳ 번역을 진행 중입니다. 잠시 후 '1'을 입력해 주세요!"
            threading.Thread(target=fetch_gemini, args=(user_msg,), daemon=True).strip = None
            
            # 제미나이 실시간 호출 (3초 이내에 끝나면 바로 보여주고, 길어지면 대기 안내 후 '1'로 꺼내봅니다)
            try:
                prompt = (
                    "한국어-따갈로그어(Taglish) 전문 통역사로서 3줄 이내로 핵심만 번역해줘.\n"
                    f"입력 문장: {user_msg}"
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": 200, "temperature": 0.2, "thinkingConfig": {"thinkingBudget": 0}}
                }
                res = session.post(url, json=payload, timeout=3.5)
                data = res.json()
                if "candidates" in data and len(data["candidates"]) > 0:
                    answer = "📝 [실시간 번역 결과]\n\n" + data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    LAST_RESULT["text"] = answer
                else:
                    answer = "⏳ 문장이 길어 번역 중입니다. 3초 뒤에 '1'을 입력해 주세요!"
            except Exception:
                answer = "⏳ 문장이 길어 번역 중입니다. 3초 뒤에 '1'을 입력해 주세요!"

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
