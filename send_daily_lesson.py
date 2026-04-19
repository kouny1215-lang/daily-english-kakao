"""
Daily English Lesson - Kakao Self-Message Sender (v2)

매일 아침 랜덤하게 선택된 영어 레슨을 카카오톡 '나에게 보내기'로 발송합니다.
GitHub Actions cron으로 실행됩니다.

필요한 환경변수 (GitHub Secrets):
- KAKAO_REST_API_KEY: 카카오 앱의 REST API 키
- KAKAO_CLIENT_SECRET: 카카오 앱의 Client Secret
- KAKAO_REFRESH_TOKEN: 최초 인증 후 받은 refresh token
"""

import json
import os
import random
import sys
from datetime import datetime, timezone, timedelta

import requests


KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_MESSAGE_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"


def refresh_access_token(rest_api_key: str, client_secret: str, refresh_token: str) -> str:
    """Refresh token으로 새 access token을 발급받습니다."""
    data = {
        "grant_type": "refresh_token",
        "client_id": rest_api_key,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }

    response = requests.post(KAKAO_TOKEN_URL, data=data, timeout=10)
    response.raise_for_status()
    result = response.json()

    access_token = result.get("access_token")
    if not access_token:
        raise RuntimeError(f"Failed to refresh token: {result}")

    return access_token


def pick_lesson(lessons_path: str) -> dict:
    """레슨 데이터에서 오늘의 레슨을 랜덤 선택합니다."""
    with open(lessons_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lessons = data["lessons"]
    kst = timezone(timedelta(hours=9))
    today = datetime.now(kst).date()
    seed = today.toordinal()
    rng = random.Random(seed)
    return rng.choice(lessons)


def build_message_text(lesson: dict) -> str:
    """레슨을 200자 이내 카톡 메시지로 포맷팅합니다."""
    kst = timezone(timedelta(hours=9))
    today_str = datetime.now(kst).strftime("%m/%d")

    vocab = lesson["vocabulary"][0]
    sentence = lesson["sentences"][0]
    key_exp = lesson["keyExpression"]

    text = (
        f"📖 {today_str} · [{lesson['category']}]\n\n"
        f"🔑 {key_exp['expression']}\n"
        f"→ {key_exp['meaning']}\n\n"
        f"💡 {vocab['word']} — {vocab['meaning']}\n\n"
        f"📝 \"{sentence['en']}\"\n"
        f"→ {sentence['ko']}"
    )

    if len(text) > 200:
        text = text[:197] + "..."

    return text


def send_to_self(access_token: str, lesson: dict) -> dict:
    """카카오톡 나에게 보내기 API 호출 (text 템플릿, 200자 제한)."""
    text = build_message_text(lesson)

    template = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://kouny1215-lang.github.io/daily-english-kakao",
            "mobile_web_url": "https://kouny1215-lang.github.io/daily-english-kakao",
        },
        "button_title": "다시 보기",
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"template_object": json.dumps(template, ensure_ascii=False)}

    response = requests.post(KAKAO_MESSAGE_URL, headers=headers, data=data, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> int:
    rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    client_secret = os.environ.get("KAKAO_CLIENT_SECRET")
    refresh_token = os.environ.get("KAKAO_REFRESH_TOKEN")

    if not rest_api_key or not client_secret or not refresh_token:
        print("ERROR: Required env vars missing (KAKAO_REST_API_KEY, KAKAO_CLIENT_SECRET, KAKAO_REFRESH_TOKEN)", file=sys.stderr)
        return 1

    try:
        print("1/3 Refreshing access token...")
        access_token = refresh_access_token(rest_api_key, client_secret, refresh_token)
        print("    ✓ Token refreshed")

        print("2/3 Picking today's lesson...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        lesson = pick_lesson(os.path.join(script_dir, "lessons.json"))
        print(f"    ✓ Selected: {lesson['title']} ({lesson['category']})")

        preview = build_message_text(lesson)
        print(f"    Message length: {len(preview)} chars")
        print(f"--- Preview ---\n{preview}\n---")

        print("3/3 Sending to Kakao...")
        result = send_to_self(access_token, lesson)

        if result.get("result_code") == 0:
            print("✅ Successfully sent!")
            return 0
        else:
            print(f"❌ Send failed: {result}", file=sys.stderr)
            return 1

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"   Response: {e.response.text}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
