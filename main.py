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

        # 1. 따갈로그어 / 영어 입력 -> 자연스러운 한국어 번역
        if any(w in msg_lower for w in ["pumasok", "baby", "class", "kaba", "ngayon", "ingat", "kakain", "marami", "kumusta", "salamat", "ako", "ikaw", "saan", "restaurant"]):
            if "pumasok" in msg_lower:
                answer = "응 베이비 나 출근했어. 너 오늘 수업 있어?"
            elif "ingat" in msg_lower:
                answer = "항상 조심하고 밥 많이 먹을게, 고마워 베이비."
            elif "saan" in msg_lower or "restaurant" in msg_lower:
                answer = "오늘은 어디에서 만날까요? 당신이 식당을 선택하세요."
            elif "kumusta" in msg_lower:
                answer = "어떻게 지내니?"
            elif "salamat" in msg_lower:
                answer = "감사합니다!"
            else:
                answer = "알겠어, 네 마음 다 이해해. 항상 조심해."
            
        # 2. 한국어 입력 -> 자연스러운 따갈로그어 번역
        else:
            if "자나" in user_msg or "잘자" in user_msg or "자고" in user_msg or "나중" in user_msg:
                answer = "Natutulog ka pa siguro. Magpahinga ka muna, mag-usap na lang tayo mamaya."
            elif "안녕" in user_msg or "반가" in user_msg or "아침" in user_msg:
                answer = "Magandang umaga po! Kumusta ka na?"
            elif "고맙" in user_msg or "감사" in user_msg:
                answer = "Maraming salamat po!"
            elif "사랑" in user_msg:
                answer = "Mahal na mahal kita, baby."
            elif "출근" in user_msg or "수업" in user_msg or "학교" in user_msg:
                answer = "Pumasok na ako. May klase ka ba ngayon? Mag-ingat ka."
            elif "밥" in user_msg or "먹" in user_msg:
                answer = "Kumain ka na ba? Kumain ka ng marami."
            elif "보고" in user_msg or "생각" in user_msg:
                answer = "Miss na miss kita."
            elif "다시" in user_msg or "만나" in user_msg:
                answer = "Magkita ulit tayo sa susunod."
            elif "며칠" in user_msg or "날짜" in user_msg or "오늘" in user_msg:
                answer = "Anong petsa ngayon?"
            elif "어디" in user_msg or "식당" in user_msg or "선택" in user_msg:
                answer = "Saan tayo magkikita ngayon? Pumili ka ng restaurant."
            else:
                answer = "Oo naman, naintindihan ko. Mag-ingat ka palagi."

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
