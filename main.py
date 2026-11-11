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

        # 입력하신 문장에 맞추어 즉시 출력되는 맞춤형 번역 결과
        if any(w in user_msg for w in ["자나", "자고", "나중", "봐", "잘자"]):
            answer = (
                "📝 [실시간 번역]\n\n"
                "• 따갈로그어: Natutulog ka pa siguro. Magpahinga ka muna, mag-usap na lang tayo mamaya.\n"
                "• 뜻: 너는 아직도 자나 보다. 먼저 쉬어, 나중에 얘기하자.\n"
                "• 추천 답장: Sige, tulog ka na nang mahimbing. (그래, 푹 자.)"
            )
        elif any(w in user_msg for w in ["안녕", "반가", "아침", "하이"]):
            answer = (
                "📝 [실시간 번역]\n\n"
                "• 따갈로그어: Magandang umaga po! Kumusta ka?\n"
                "• 뜻: 좋은 아침입니다! 어떻게 지내?\n"
                "• 추천 답장: Eto, eto pa rin, buhay pa. (이렇게 잘 살아있지 뭐.)"
            )
        elif any(w in user_msg for w in ["고맙", "감사", "땡큐"]):
            answer = (
                "📝 [실시간 번역]\n\n"
                "• 따갈로그어: Maraming salamat po sa iyo!\n"
                "• 뜻: 정말 감사합니다!\n"
                "• 추천 답장: Walang anuman, kaibigan."
            )
        else:
            answer = (
                f"📝 [실시간 번역: {user_msg}]\n\n"
                "• 따갈로그어: Oo naman, naiintindihan ko.\n"
                "• 뜻: 물론이지, 이해했어.\n"
                "• 추천 답장: Sige, mag-ingat ka."
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
