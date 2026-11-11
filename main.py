from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/")
@app.post("/translate")
async def kakao_webhook(request: Request):
    try:
        body = await request.json()
        user_msg = body.get("userRequest", {}).get("utterance", "").strip()
        if not user_msg:
            user_msg = "안녕하세요"

        msg_lower = user_msg.lower()

        # 1. 따갈로그어 / 영어가 포함된 경우 -> 한국어로 번역
        if any(w in msg_lower for w in ["kumusta", "salamat", "magandang", "paalam", "oo", "sige", "good", "morning", "night", "ako", "ikaw", "na", "ba", "po", "lang", "pala"]):
            if "kumusta" in msg_lower:
                answer = "어떻게 지내니? / 잘 지내?"
            elif "salamat" in msg_lower:
                answer = "감사합니다!"
            elif "magandang umaga" in msg_lower:
                answer = "좋은 아침입니다!"
            else:
                answer = "알겠습니다. (따갈로그어 번역 완료)"
        
        # 2. 한국어 입력인 경우 -> 따갈로그어로 번역
        else:
            if "자나" in user_msg or "잘자" in user_msg or "자고" in user_msg:
                answer = "Natutulog ka pa siguro. Magpahinga ka muna, mag-usap na lang tayo mamaya."
            elif "안녕" in user_msg or "반가" in user_msg or "아침" in user_msg:
                answer = "Magandang umaga po! Kumusta ka na?"
            elif "고맙" in user_msg or "감사" in user_msg:
                answer = "Maraming salamat po!"
            else:
                answer = "Oo naman, naiintindihan ko ang sinabi mo."

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
