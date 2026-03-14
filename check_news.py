import requests
import os
from bs4 import BeautifulSoup

NEWS_URL = "https://produce101.jp/news/1/"

def get_latest_news():
    r = requests.get(NEWS_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    a = soup.select_one('a[href*="/news/detail/"]')
    title = a.text.strip()
    link = "https://produce101.jp" + a["href"]

    return title, link


def send_line(message):

    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    user_id = os.environ["LINE_USER_ID"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "to": user_id,
        "messages":[
            {"type":"text","text":message}
        ]
    }

    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=data
    )


title, link = get_latest_news()

send_line(f"🔔 PRODUCE101更新\n\n{title}\n\n{link}")
