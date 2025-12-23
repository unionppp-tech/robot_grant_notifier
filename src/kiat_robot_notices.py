# src/kiat_robot_notices.py
import subprocess
import sys
import datetime

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import requests
except ImportError:
    install("requests")
    import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    install("beautifulsoup4")
    from bs4 import BeautifulSoup

import os
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_message(msg: str):
    now = datetime.datetime.now()
    payload = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Discord send failed: {e}")
    print(msg)

def fetch_kiat_robot_notices(recent_days=7):
    url = "https://www.kiat.or.kr/site/notice/list"
    params = {"keyword": "로봇"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except Exception as e:
        send_message(f"KIAT 접속 실패: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    notices = soup.select("div.notice-list > ul > li")
    today = datetime.datetime.today()
    results = []

    for notice in notices:
        title_tag = notice.select_one("a")
        date_tag = notice.select_one("span.date")
        if not title_tag or not date_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = "https://www.kiat.or.kr" + title_tag.get("href")
        date_text = date_tag.get_text(strip=True)
        try:
            pub_date = datetime.datetime.strptime(date_text, "%Y-%m-%d")
        except:
            continue

        if (today - pub_date).days <= recent_days:
            results.append(f"{title} ({date_text})\n{link}")

    return results

if __name__ == "__main__":
    notices = fetch_kiat_robot_notices()
    if not notices:
        send_message("최근 로봇 관련 KIAT 공모사업 공고가 없습니다.")
    else:
        for notice in notices:
            send_message(notice)
