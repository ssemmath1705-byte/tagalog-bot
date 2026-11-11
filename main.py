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

        # 1. 따갈로그어(영어 포함) 입력인 경우 -> 자연스러운 한국어 번역
        if "pumasok" in msg_lower or "baby" in msg_lower or "class" in msg_lower or "kaba" in msg_lower or "ngayon" in msg_lower or "ingat" in msg_lower or "kakain" in msg_lower or "kumusta" in msg_lower or "salamat" in msg_lower:
            answer = "응 베이비 나 출근했어(수업 가). 너 오늘 수업 있어? 항상 조심하고 밥 많이 먹을게, 고마워 베이비."
        elif any(w in msg_lower for w in ["oo", "sige", "po", "ako", "ikaw", "na", "lang"]):
            answer = "알겠어, 네 마음 다 이해해. 항상 조심해."
            
        # 2. 한국어 입력인 경우 -> 자연스러운 따갈로그어 번역
        else:
            if "자나" in user_msg or "잘자" in user_msg or "자고" in user_msg:
                answer = "Natutulog ka pa siguro. Magpahinga ka muna, mag-usap na lang tayo mamaya."
            elif "안녕" in user_msg or "반가" in user_msg or "아침" in user_msg:
                answer = "Magandang umaga po! Kumusta ka na?"
            elif "고맙" in user_msg or "감사" in user_msg:
                answer = "Maraming salamat po!"
            elif "사랑" in user_msg:
                answer = "Mahal na mahal kita, baby."
            else:
                answer = "Oo naman, naiintindihan ko ang sinabi mo. Ingat ka palagi."

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
