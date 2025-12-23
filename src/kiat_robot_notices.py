#!/usr/bin/env python3
import subprocess
import sys
import datetime

# =========================
# 필수 라이브러리 설치
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
import os
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# =========================
# 디스코드 메시지 전송
# =========================
def send_message(msg: str):
    now = datetime.datetime.now()
    payload = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Discord send failed: {e}")
    print(msg)

# =========================
# 로봇 관련 공고 크롤링
# =========================
def fetch_robot_public_projects(keyword="로봇"):
    base_url = "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    params = {
        "searchField": "all",
        "searchText": keyword,
        "pageIndex": "1"
    }

    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=10)
        if resp.status_code != 200:
            send_message(f"❌ 공고 페이지 요청 실패: status={resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        rows = soup.select("div.board-list table tbody tr")

        results = []
        for row in rows:
            # 공고 제목
            title_tag = row.select_one("td a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://www.bizinfo.go.kr" + title_tag.get("href")
            # 날짜
            date_tag = row.select_one("td:nth-child(5)")
            date_str = date_tag.get_text(strip=True) if date_tag else ""

            # 키워드 필터 (로봇 포함)
            if keyword in title:
                results.append(f"{date_str} | {title}\n{link}")

        return results

    except Exception as e:
        send_message(f"❌ 크롤링 에러: {e}")
        return []

# =========================
# 메인 실행
# =========================
if __name__ == "__main__":
    notices = fetch_robot_public_projects("로봇")
    if not notices:
        send_message("🤖 로봇 공공사업 공고를 찾지 못했습니다.")
    else:
        send_message("🤖 최신 로봇 공공사업 공고:")
        for notice in notices:
            send_message(notice)
