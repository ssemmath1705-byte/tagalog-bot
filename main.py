from fastapi import FastAPI, Request
import requests
import threading

app = FastAPI()
session = requests.Session()

GEMINI_API_KEY = "AQ.Ab8RN6JB2PByMqHn-r3MFsfPTWRvjvPBAwKlaCbJLZkKQVPw0g"
CACHE = {}
LAST_RESULT = {}

def make_prompt(user_msg: str) -> str:
    return (
        "한국어-따갈로그어(Taglish) 통역사로서 카톡에서 읽기 편하게 4줄 이내로 핵심만 답해줘.\n"
        "1. [한국어] 입력 시: 자연스러운 따갈로그어/Taglish 표현 2개와 (한글 발음)\n"
        "2. [따갈로그어/영어] 입력 시: 한국어 뜻과 짧은 추천 답장 1개(한글 발음 포함)\n"
        f"문장: {user_msg}"
    )

def call_single_model(model_name: str, prompt: str, use_thinking_zero: bool, timeout_sec: float):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    gen_config = {"maxOutputTokens": 250, "temperature": 0.2}
    if use_thinking_zero:
        gen_config["thinkingConfig"] = {"thinkingBudget": 0}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": gen_config
    }
    res = session.post(url, json=payload, timeout=timeout_sec)
    return res.json()

def request_gemini(user_msg: str, timeout_sec: float = 3.8) -> str:
    prompt = make_prompt(user_msg)
    for model_name in ["gemini-3.8-flash", "gemini-flash-latest"]:
        for use_zero in [True, False]:
            try:
                data = call_single_model(model_name, prompt, use_zero, timeout_sec)
                if "candidates" in data and len(data["candidates"]) > 0:
                    ans = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    CACHE[user_msg] = ans
                    LAST_RESULT["text"] = f"📝 [{user_msg}]\n\n{ans}"
                    return ans
                err = data.get("error", {}).get("message", "")
                if "not found" in err.lower() or "no longer available" in err.lower():
                    break
            except requests.exceptions.Timeout:
                raise
            except Exception:
                continue
    return "API 모델 응답 확인 필요"

def bg_translate(user_msg: str):
    try:
        request_gemini(user_msg, timeout_sec=15.0)
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

        if user_msg in [".", "결과", "다시", "1"]:
            answer = LAST_RESULT.get("text", "아직 완료된 이전 번역이 없습니다. 조금만 더 기다렸다 입력해 주세요.")
        elif user_msg in CACHE:
            answer = CACHE[user_msg]
        else:
            try:
                answer = request_gemini(user_msg, timeout_sec=3.8)
            except requests.exceptions.Timeout:
                threading.Thread(target=bg_translate, args=(user_msg,), daemon=True).start()
                answer = "⏳ 문장이 길어 번역 중입니다. 3초 뒤에 점(.)이나 1을 입력하시면 번역 결과를 바로 보여드릴게요!"
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
