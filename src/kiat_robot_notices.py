#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import os
import datetime

# =========================
# 라이브러리 자동 설치
# =========================
def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

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
# 디스코드 전송
# =========================
def send_message(msg):
    now = datetime.datetime.now()
    payload = {"content": f"[{now:%Y-%m-%d %H:%M:%S}] {msg}"}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
    print(msg)

# =========================
# 기업마당 공공사업공고 크롤링
# =========================
def fetch_public_notices(max_count=5):
    url = "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)
    if res.status_code != 200:
        send_message(f"❌ 기업마당 접속 실패 (status={res.status_code})")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("div.board-list table tbody tr")

    results = []
    for row in rows:
        title_tag = row.select_one("td a")
        date_tag = row.select_one("td:last-child")

        if not title_tag or not date_tag:
            continue

        title = title_tag.get_text(strip=True)
        date = date_tag.get_text(strip=True)
        link = "https://www.bizinfo.go.kr" + title_tag.get("href", "")

        # ✅ 핵심 필터: '공고'라는 단어가 들어간 것만
        if "공고" in title:
            results.append(f"{date} | {title}\n{link}")

        if len(results) >= max_count:
            break

    return results

# =========================
# 메인
# =========================
if __name__ == "__main__":
    notices = fetch_public_notices()

    if not notices:
        send_message("📭 오늘 기준 공공사업 공고를 찾지 못했습니다.")
    else:
        send_message("📢 오늘의 공공사업 공고")
        for n in notices:
            send_message(n)
