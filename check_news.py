import os
import json
import re
import requests
from bs4 import BeautifulSoup

NEWS_URL = "https://produce101.jp/news/1/"
STATE_FILE = "state.json"
LINE_PUSH_API = "https://api.line.me/v2/bot/message/push"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_latest_news():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(NEWS_URL, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    a = soup.select_one('a[href*="/news/detail/"]')

    if not a:
        raise RuntimeError("最新記事リンクが見つかりませんでした。")

    href = a.get("href", "")
    title = a.get_text(" ", strip=True)

    match = re.search(r"/news/detail/(\\d+)", href)
    if not match:
        raise RuntimeError(f"記事IDを取得できませんでした: {href}")

    news_id = match.group(1)
    url = "https://produce101.jp" + href if href.startswith("/") else href

    return {
        "id": news_id,
        "title": title,
        "url": url
    }

def send_line_message(text):
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    r = requests.post(LINE_PUSH_API, headers=headers, json=payload, timeout=20)
    r.raise_for_status()

def main():
    state = load_state()
    latest = get_latest_news()

    last_id = state.get("last_id")
    if last_id != latest["id"]:
        message = f"🔔 PRODUCE 101 NEWS更新\\n\\n{latest['title']}\\n\\n{latest['url']}"
        send_line_message(message)

        state["last_id"] = latest["id"]
        save_state(state)
        print("Updated and notified:", latest["id"])
    else:
        print("No update:", latest["id"])

if __name__ == "__main__":
    main()
