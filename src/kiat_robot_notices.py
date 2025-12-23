#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import os
import datetime

# =========================
# 라이브러리 자동 설치
# =========================
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

# =========================
# 환경 변수
# =========================
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# =========================
# 디스코드 메시지 전송
# =========================
def send_message(msg: str):
    now = datetime.datetime.now()
    payload = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"}
    requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    print(msg)

# =========================
# KIAT 로봇 공모사업 공고
# =========================
def get_kiat_robot_notices(max_count=5):
    url = "https://www.kiat.or.kr/site/kiat/ex/bbs/List.do?cbIdx=277"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        send_message(f"❌ KIAT 접속 실패 (status={res.status_code})")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("table tbody tr")

    results = []
    for row in rows:
        title_tag = row.select_one("td.subject a")
        date_tag = row.select_one("td.date")

        if not title_tag or not date_tag:
            continue

        title = title_tag.get_text(strip=True)
        date = date_tag.get_text(strip=True)
        link = "https://www.kiat.or.kr" + title_tag.get("href")

        if "로봇" in title or "robot" in title.lower():
            results.append(f"{date} | {title}\n{link}")

        if len(results) >= max_count:
            break

    return results

# =========================
# 메인 실행
# =========================
if __name__ == "__main__":
    notices = get_kiat_robot_notices()

    if not notices:
        send_message("🤖 KIAT 최근 로봇 관련 공모사업 공고가 없습니다.")
    else:
        send_message("🤖 KIAT 로봇 관련 공모사업 공고")
        for n in notices:
            send_message(n)
