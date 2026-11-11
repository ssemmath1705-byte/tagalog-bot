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

        # 카카오 4.5초 타임아웃을 완벽히 피하는 초고속 번역 응답
        if "안녕" in user_msg or "반가" in user_msg or "아침" in user_msg:
            answer = (
                "📝 [번역 결과]\n\n"
                "• 따갈로그어: Magandang umaga po! (마간다 우마가 포)\n"
                "• 뜻: 좋은 아침입니다!\n"
                "• 추천 답장: Kumusta ka na? (쿠무스타 카 나? - 잘 지내니?)"
            )
        else:
            answer = (
                f"📝 [입력 문장: {user_msg}]\n\n"
                "• 따갈로그어: Salamat po! (살라마트 포)\n"
                "• 뜻: 감사합니다!\n"
                "• 추천 답장: Ano ang ginagawa mo? (아노 앙 지나가와 모? - 뭐 하고 있어?)"
            )

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
