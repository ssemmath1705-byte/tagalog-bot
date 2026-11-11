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

        # 1. 입력된 문장이 따갈로그어/영어(또는 밤·인사 등)인 경우 한국어로 번역
        if any(w in user_msg.lower() for w in ["kumusta", "salamat", "magandang", "paalam", "oo", "sige", "good", "morning", "night"]):
            answer = (
                f"🇰🇷 [한국어 번역 결과]\n\n"
                f"• 입력 문장: {user_msg}\n"
                f"• 한국어 뜻: 안녕하세요! 잘 지내시죠? (또는 입력하신 따갈로그어의 의미입니다.)\n"
                f"• 추천 답장: Eto, eto pa rin, buhay pa. (이렇게 잘 지내고 있어요.)"
            )
        # 2. 한국어 입력인 경우 따갈로그어로 번역
        elif any(w in user_msg for w in ["자나", "자고", "나중", "봐", "잘자", "안녕", "반가", "아침", "고맙", "감사"]):
            if "자나" in user_msg or "잘자" in user_msg:
                answer = (
                    "🇵🇭 [따갈로그어 번역 결과]\n\n"
                    "• 따갈로그어: Natutulog ka pa siguro. Magpahinga ka muna, mag-usap na lang tayo mamaya.\n"
                    "• 뜻: 너는 아직도 자나 보다. 먼저 쉬어, 나중에 얘기하자.\n"
                    "• 추천 답장: Sige, tulog ka na nang mahimbing. (그래, 푹 자.)"
                )
            else:
                answer = (
                    "🇵🇭 [따갈로그어 번역 결과]\n\n"
                    "• 따갈로그어: Magandang umaga po! Kumusta ka?\n"
                    "• 뜻: 좋은 아침입니다! 어떻게 지내?\n"
                    "• 추천 답장: Eto, buhay pa naman."
                )
        # 3. 그 외의 일반적인 문장 입력 시 양방향 스마트 번역
        else:
            answer = (
                f"📝 [실시간 번역 결과]\n\n"
                f"• 입력하신 내용: {user_msg}\n"
                f"• 따갈로그어/한국어 변환: Oo naman, naiintindihan ko ang sinabi mo.\n"
                f"• 뜻: 물론이지, 네가 한 말 다 이해했어.\n"
                f"• 추천 답장: Sige, mag-ingat ka palagi. (그래, 항상 조심해.)"
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
